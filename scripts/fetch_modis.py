#!/usr/bin/env python3
"""NASA MOD13Q1 AppEEARS ingestion and 199-district quality-screened zonal statistics."""
from __future__ import annotations

import argparse
import concurrent.futures
import hashlib
import json
import os
import re
import tempfile
import time
from collections import defaultdict
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np
import rasterio
import requests
from rasterio.mask import mask as raster_mask
from rasterio.merge import merge
from rasterio.warp import transform_geom
from shapely.geometry import mapping, shape
from shapely.ops import unary_union

API = "https://appeears.earthdatacloud.nasa.gov/api/"
PRODUCT = "MOD13Q1.061"
FILE_PATTERN = re.compile(r"MOD13Q1\.061.*?(NDVI|EVI|VI_Quality)_doy(\d{7}).*?\.tif$", re.IGNORECASE)
VALID_MIN, VALID_MAX, FILL_VALUE, SCALE_FACTOR = -2000, 10000, -3000, 0.0001
QUALITY_POLICY = (
    "MOD13Q1 VI_Quality: VI quality bits 0-1 == 0; VI usefulness bits 2-5 <= 8; "
    "adjacent-cloud bit 8 == 0; mixed-cloud bit 10 == 0; land/water bits 11-13 == 1; "
    "possible-snow bit 14 == 0; possible-shadow bit 15 == 0. "
    "NDVI/EVI valid DN range -2000..10000, fill -3000, scale factor 0.0001. "
    "Project usability threshold: >=10 good pixels and good/candidate fraction >=0.20."
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--boundaries", type=Path, required=True)
    parser.add_argument("--output", type=Path, default=Path("data/modis/UZB_ADM2_MOD13Q1.json"))
    parser.add_argument("--start-date", required=True, help="YYYY-MM-DD inclusive")
    parser.add_argument("--end-date", required=True, help="YYYY-MM-DD inclusive")
    parser.add_argument("--poll-seconds", type=int, default=30)
    parser.add_argument("--max-wait-seconds", type=int, default=21600)
    parser.add_argument("--download-workers", type=int, default=6)
    return parser.parse_args()


def parse_date(value: str) -> date:
    try:
        return datetime.strptime(value, "%Y-%m-%d").date()
    except ValueError as exc:
        raise ValueError(f"Sana YYYY-MM-DD bo‘lishi kerak: {value}") from exc


def read_boundaries(path: Path) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if payload.get("type") != "FeatureCollection":
        raise RuntimeError("ADM2 GeoJSON FeatureCollection emas.")
    result, seen = [], set()
    for feature in payload.get("features") or []:
        props = feature.get("properties") or {}
        area_id = str(props.get("shapeID") or props.get("shape_id") or "").strip()
        name = str(props.get("shapeName") or props.get("shape_name") or props.get("NAME_2") or "").strip()
        geometry = feature.get("geometry")
        if not area_id or not name or not geometry:
            raise RuntimeError("ADM2 qatlamida shapeID/nom/geometriya yetishmaydi.")
        if area_id in seen:
            raise RuntimeError(f"ADM2 shapeID takrorlangan: {area_id}")
        seen.add(area_id)
        geom = shape(geometry)
        if geom.is_empty:
            raise RuntimeError(f"Bo‘sh ADM2 geometriya: {area_id}")
        if not geom.is_valid:
            geom = geom.buffer(0)
        if geom.is_empty or not geom.is_valid:
            raise RuntimeError(f"Yaroqsiz geometriya tuzatilmadi: {area_id}")
        result.append({"shape_id": area_id, "name": name, "geometry": geom})
    if len(result) != 199:
        raise RuntimeError(f"199 ta ADM2 kutilgan, {len(result)} ta topildi.")
    result.sort(key=lambda row: row["shape_id"])
    return result, payload


def build_country_aoi(features: list[dict[str, Any]]) -> dict[str, Any]:
    union = unary_union([row["geometry"] for row in features])
    if union.is_empty:
        raise RuntimeError("ADM2 union geometriya bo‘sh.")
    if not union.is_valid:
        union = union.buffer(0)
    # Only the NASA clip geometry is simplified. Zonal calculations use original ADM2 shapes.
    union = union.simplify(0.0002, preserve_topology=True)
    return {
        "type": "FeatureCollection",
        "crs": {"type": "name", "properties": {"name": "urn:ogc:def:crs:OGC::CRS84"}},
        "features": [{
            "type": "Feature", "id": "UZB-ADM2-UNION",
            "properties": {"name": "Uzbekistan ADM2 union"},
            "geometry": mapping(union),
        }],
    }


def api_headers(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}", "Accept": "application/json"}


def login(session: requests.Session, username: str, password: str) -> str:
    response = session.post(API + "login", auth=(username, password), timeout=(30, 120))
    if response.status_code == 401:
        raise RuntimeError("NASA Earthdata Login noto‘g‘ri yoki AppEEARS ruxsati yo‘q.")
    response.raise_for_status()
    token = response.json().get("token")
    if not token:
        raise RuntimeError("AppEEARS login javobida Bearer token topilmadi.")
    return str(token)


def submit_task(session: requests.Session, token: str, geo: dict[str, Any], start: date, end: date) -> str:
    task = {
        "task_type": "area",
        "task_name": f"OSH-UZB-MOD13Q1-{start:%Y%m%d}-{end:%Y%m%d}",
        "params": {
            "dates": [{"startDate": start.strftime("%m-%d-%Y"), "endDate": end.strftime("%m-%d-%Y")}],
            "layers": [
                {"product": PRODUCT, "layer": "_250m_16_days_NDVI"},
                {"product": PRODUCT, "layer": "_250m_16_days_EVI"},
            ],
            "output": {"format": {"type": "geotiff"}, "projection": "native"},
            "geo": geo,
        },
    }
    response = session.post(API + "task", json=task, headers=api_headers(token), timeout=(60, 300))
    response.raise_for_status()
    task_id = response.json().get("task_id")
    if not task_id:
        raise RuntimeError(f"AppEEARS task javobida task_id yo‘q: {response.text[:1000]}")
    print(f"[NASA] AppEEARS task yuborildi: {task_id}", flush=True)
    return str(task_id)


def wait_for_task(session: requests.Session, token: str, task_id: str, poll_seconds: int, max_wait_seconds: int) -> None:
    deadline = time.monotonic() + max_wait_seconds
    while time.monotonic() < deadline:
        response = session.get(API + f"task/{task_id}", headers=api_headers(token), timeout=(30, 120))
        response.raise_for_status()
        result = response.json()
        status = str(result.get("status") or "").lower()
        print(f"[NASA] task={task_id} status={status}", flush=True)
        if status == "done":
            return
        if status in {"failed", "error", "cancelled"}:
            raise RuntimeError(f"AppEEARS task muvaffaqiyatsiz: {json.dumps(result)[:2000]}")
        time.sleep(max(5, poll_seconds))
    raise TimeoutError(f"AppEEARS task {task_id} {max_wait_seconds} sekund ichida tugamadi.")


def list_bundle_files(session: requests.Session, token: str, task_id: str) -> list[dict[str, Any]]:
    response = session.get(API + f"bundle/{task_id}", headers=api_headers(token), timeout=(30, 180))
    response.raise_for_status()
    files = response.json().get("files") or []
    selected = [
        item for item in files
        if str(item.get("file_name") or "").lower().endswith(".tif")
        and FILE_PATTERN.search(Path(str(item.get("file_name"))).name)
    ]
    if not selected:
        raise RuntimeError("AppEEARS bundle ichida MOD13Q1 NDVI/EVI/VI_Quality GeoTIFF topilmadi.")
    return selected


def download_one(task_id: str, item: dict[str, Any], token: str, directory: Path) -> Path:
    file_id = str(item["file_id"])
    name = Path(str(item["file_name"])).name
    target = directory / name
    response = requests.get(
        API + f"bundle/{task_id}/{file_id}",
        headers=api_headers(token), stream=True, allow_redirects=True, timeout=(60, 600),
    )
    response.raise_for_status()
    digest = hashlib.sha256()
    with target.open("wb") as output:
        for chunk in response.iter_content(chunk_size=1024 * 1024):
            if chunk:
                digest.update(chunk)
                output.write(chunk)
    expected = item.get("sha256")
    if expected and digest.hexdigest().lower() != str(expected).lower():
        target.unlink(missing_ok=True)
        raise RuntimeError(f"SHA256 checksum mos emas: {name}")
    return target


def good_modis_quality(qa: np.ndarray) -> np.ndarray:
    values = qa.astype(np.int64, copy=False)
    return (
        (values >= 0) & (values < 65535)
        & ((values & 0b11) == 0)
        & (((values >> 2) & 0b1111) <= 8)
        & (((values >> 8) & 1) == 0)
        & (((values >> 10) & 1) == 0)
        & (((values >> 11) & 0b111) == 1)
        & (((values >> 14) & 1) == 0)
        & (((values >> 15) & 1) == 0)
    )


def mosaic_tiles(paths: list[Path], output: Path) -> Path:
    if len(paths) == 1:
        return paths[0]
    datasets = [rasterio.open(path) for path in paths]
    try:
        if len({str(ds.crs) for ds in datasets}) != 1:
            raise RuntimeError("MODIS tile CRS mos emas.")
        array, transform = merge(datasets, nodata=datasets[0].nodata)
        profile = datasets[0].profile.copy()
        profile.update(driver="GTiff", height=array.shape[1], width=array.shape[2],
                       transform=transform, count=array.shape[0], compress="deflate")
        with rasterio.open(output, "w", **profile) as dst:
            dst.write(array)
    finally:
        for dataset in datasets:
            dataset.close()
    return output


def masked_pixels(dataset: rasterio.io.DatasetReader, geometry: dict[str, Any]) -> tuple[np.ndarray, np.ndarray]:
    image, _ = raster_mask(dataset, [geometry], crop=True, filled=False, all_touched=False)
    band = image[0]
    raw = np.asarray(band.data)
    valid = ~np.ma.getmaskarray(band)
    if dataset.nodata is not None:
        valid &= raw != dataset.nodata
    return raw, valid


def scaled_values(raw: np.ndarray, valid: np.ndarray, dataset: rasterio.io.DatasetReader) -> np.ndarray:
    factor = float(dataset.scales[0]) if dataset.scales else 1.0
    if factor == 1.0 and raw.dtype.kind in {"i", "u"}:
        factor = SCALE_FACTOR
    return raw.astype(np.float64, copy=False)[valid] * factor


def summarize_district(ndvi_path: Path, evi_path: Path, qa_path: Path, geometry: dict[str, Any]) -> dict[str, Any]:
    empty = {
        "ndvi_mean": None, "ndvi_p90": None, "ndvi_max": None,
        "evi_mean": None, "evi_p90": None, "evi_max": None,
        "candidate_pixel_count": 0, "good_pixel_count": 0,
        "good_pixel_fraction": None, "quality_usable": False,
    }
    with rasterio.open(ndvi_path) as ndvi, rasterio.open(evi_path) as evi, rasterio.open(qa_path) as qa:
        if not ndvi.crs or evi.crs != ndvi.crs or qa.crs != ndvi.crs:
            raise RuntimeError("MODIS NDVI/EVI/VI_Quality CRS mos emas.")
        if ndvi.transform != evi.transform or ndvi.transform != qa.transform:
            raise RuntimeError("MODIS NDVI/EVI/VI_Quality raster panjaralari mos emas.")
        projected = transform_geom("EPSG:4326", ndvi.crs, geometry, precision=-1)
        try:
            n_raw, n_inside = masked_pixels(ndvi, projected)
            e_raw, e_inside = masked_pixels(evi, projected)
            q_raw, q_inside = masked_pixels(qa, projected)
        except ValueError:
            return empty
        if n_raw.shape != e_raw.shape or n_raw.shape != q_raw.shape:
            raise RuntimeError("MODIS NDVI/EVI/VI_Quality shape mos emas.")
        n_valid = n_inside & (n_raw >= VALID_MIN) & (n_raw <= VALID_MAX) & (n_raw != FILL_VALUE)
        e_valid = e_inside & (e_raw >= VALID_MIN) & (e_raw <= VALID_MAX) & (e_raw != FILL_VALUE)
        q_valid = q_inside & (q_raw >= 0) & (q_raw < 65535)
        candidate = n_valid & e_valid & q_valid
        good = candidate & good_modis_quality(q_raw)
        candidate_count, good_count = int(np.count_nonzero(candidate)), int(np.count_nonzero(good))
        if candidate_count == 0 or good_count == 0:
            empty["candidate_pixel_count"] = candidate_count
            empty["good_pixel_count"] = good_count
            empty["good_pixel_fraction"] = 0.0 if candidate_count else None
            return empty
        n_values, e_values = scaled_values(n_raw, good, ndvi), scaled_values(e_raw, good, evi)
        fraction = good_count / candidate_count
        return {
            "ndvi_mean": round(float(np.mean(n_values)), 6),
            "ndvi_p90": round(float(np.percentile(n_values, 90)), 6),
            "ndvi_max": round(float(np.max(n_values)), 6),
            "evi_mean": round(float(np.mean(e_values)), 6),
            "evi_p90": round(float(np.percentile(e_values, 90)), 6),
            "evi_max": round(float(np.max(e_values)), 6),
            "candidate_pixel_count": candidate_count,
            "good_pixel_count": good_count,
            "good_pixel_fraction": round(fraction, 6),
            "quality_usable": bool(good_count >= 10 and fraction >= 0.20),
        }


def load_existing_areas(path: Path) -> tuple[dict[str, Any], dict[str, Any]]:
    if not path.is_file():
        return {}, {}
    payload = json.loads(path.read_text(encoding="utf-8"))
    if payload.get("country_iso3") != "UZB" or payload.get("product_id") != PRODUCT:
        raise RuntimeError("Mavjud MODIS zonal fayl identity metadata mos emas.")
    return payload, payload.get("areas") or {}


def main() -> int:
    args = parse_args()
    start, end = parse_date(args.start_date), parse_date(args.end_date)
    if start > end:
        raise ValueError("start-date end-date dan keyin bo‘lishi mumkin emas.")
    if (end - start).days > 550:
        raise ValueError("Bitta AppEEARS so‘rovi 550 kundan oshmasin; tarixni bo‘laklab yuklang.")
    username = os.environ.get("NASA_EARTHDATA_USERNAME", "").strip()
    password = os.environ.get("NASA_EARTHDATA_PASSWORD", "")
    if not username or not password:
        raise RuntimeError("GitHub Actions Secrets: NASA_EARTHDATA_USERNAME va NASA_EARTHDATA_PASSWORD kerak.")

    districts, _ = read_boundaries(args.boundaries)
    geo = build_country_aoi(districts)
    session = requests.Session()
    token = login(session, username, password)
    task_id = submit_task(session, token, geo, start, end)
    wait_for_task(session, token, task_id, args.poll_seconds, args.max_wait_seconds)
    bundle = list_bundle_files(session, token, task_id)
    print(f"[NASA] {len(bundle)} ta MODIS GeoTIFF yuklanadi.", flush=True)

    with tempfile.TemporaryDirectory(prefix="osh-modis-") as temporary:
        temp = Path(temporary)
        worker_count = max(1, min(args.download_workers, 8))
        with concurrent.futures.ThreadPoolExecutor(max_workers=worker_count) as pool:
            futures = [pool.submit(download_one, task_id, item, token, temp) for item in bundle]
            downloaded = [future.result() for future in concurrent.futures.as_completed(futures)]

        grouped: dict[str, dict[str, list[Path]]] = defaultdict(lambda: defaultdict(list))
        dates: dict[str, date] = {}
        for path in downloaded:
            match = FILE_PATTERN.search(path.name)
            if not match:
                continue
            layer, doy = match.group(1).upper(), match.group(2)
            grouped[doy][layer].append(path)
            dates[doy] = datetime.strptime(doy, "%Y%j").date()

        if not grouped:
            raise RuntimeError("AppEEARS bundle’da MOD13Q1 kompozitlari yo‘q.")
        composite_paths = {}
        for doy, layer_files in grouped.items():
            missing = {"NDVI", "EVI", "VI_QUALITY"} - set(layer_files)
            if missing:
                raise RuntimeError(f"{doy} kompozitida qatlam yetishmaydi: {sorted(missing)}")
            composite_paths[doy] = {
                layer: mosaic_tiles(paths, temp / f"{doy}_{layer}_mosaic.tif")
                for layer, paths in layer_files.items()
            }

        output_path = args.output.resolve()
        output_path.parent.mkdir(parents=True, exist_ok=True)
        old_payload, old_areas = load_existing_areas(output_path)
        areas = {}
        for district in districts:
            old_area = old_areas.get(district["shape_id"]) or {}
            observations = {row["date"]: row for row in (old_area.get("observations") or [])}
            areas[district["shape_id"]] = {"name_uz": district["name"], "observations": observations}

        for doy in sorted(composite_paths):
            layers = composite_paths[doy]
            observation_date = dates[doy]
            for district in districts:
                stats = summarize_district(
                    layers["NDVI"], layers["EVI"], layers["VI_QUALITY"], mapping(district["geometry"])
                )
                row = {"date": observation_date.isoformat(), "year": observation_date.year,
                       "julian_day": int(doy[-3:]), **stats}
                areas[district["shape_id"]]["observations"][observation_date.isoformat()] = row
            print(f"[ZONAL] {observation_date.isoformat()} · 199 tuman hisoblandi.", flush=True)

        serial_areas = {
            area_id: {"name_uz": area["name_uz"],
                      "observations": sorted(area["observations"].values(), key=lambda row: row["date"])}
            for area_id, area in areas.items()
        }
        all_dates = [row["date"] for area in serial_areas.values() for row in area["observations"]]
        if not all_dates:
            raise RuntimeError("Hech qanday MODIS kuzatuvi hisoblanmadi.")
        history = list((old_payload or {}).get("ingestion_history") or [])
        history.append({
            "task_id": task_id, "start_date": start.isoformat(), "end_date": end.isoformat(),
            "downloaded_geotiff_count": len(downloaded), "composite_count": len(grouped),
            "completed_at_utc": datetime.now(timezone.utc).isoformat(),
        })
        payload = {
            "product": "MODIS/Terra Vegetation Indices 16-Day L3 Global 250m SIN Grid",
            "product_id": PRODUCT, "collection": "061", "country_iso3": "UZB", "admin_level": "ADM2",
            "source": "NASA LP DAAC via AppEEARS", "doi": "10.5067/MODIS/MOD13Q1.061",
            "source_resolution": "250 m", "temporal_resolution": "16 day",
            "output_projection": "MODIS native sinusoidal", "value_scale_factor": SCALE_FACTOR,
            "quality_policy": QUALITY_POLICY, "boundary_source": "geoBoundaries UZB ADM2",
            "aggregation": "199 original ADM2 polygons; union used only for country clip",
            "observation_date_range": {"start": min(all_dates), "end": max(all_dates)},
            "ingestion_history": history, "generated_at_utc": datetime.now(timezone.utc).isoformat(),
            "areas": serial_areas,
        }
        temp_out = output_path.with_suffix(".json.tmp")
        temp_out.write_text(json.dumps(payload, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
        temp_out.replace(output_path)
    print(f"[OK] MODIS dataset: {output_path} · 199 tuman · {len(grouped)} kompozit")
    print(f"[OK] AppEEARS task: {task_id}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
