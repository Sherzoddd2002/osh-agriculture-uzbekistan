#!/usr/bin/env python3
"""Build and validate the public Uzbekistan-only data bundle for GitHub Pages.

Only openly licensed public aggregates and boundary files are downloaded.
No user files, private database rows, credentials or API keys are included.
"""
from __future__ import annotations

import argparse
import gzip
import json
import math
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path
from urllib.request import Request, urlopen

YEARS = tuple(range(2010, 2025))
MAPSPAM_COMMIT = "601113e0b7c948b6f19be8534a8fbe0ebec7c2ab"
BOUNDARY_COMMIT = "9469f09"

BOUNDARIES = {
    "ADM1": {
        "url": f"https://media.githubusercontent.com/media/wmgeolab/geoBoundaries/{BOUNDARY_COMMIT}/releaseData/gbOpen/UZB/ADM1/geoBoundaries-UZB-ADM1_simplified.geojson",
        "count": 14,
        "year": "2017",
        "source": "OpenStreetMap, Wambacher",
        "license": "Open Data Commons Open Database License 1.0 (ODbL 1.0)",
        "source_url": "https://www.openstreetmap.org/copyright",
    },
    "ADM2": {
        "url": f"https://media.githubusercontent.com/media/wmgeolab/geoBoundaries/{BOUNDARY_COMMIT}/releaseData/gbOpen/UZB/ADM2/geoBoundaries-UZB-ADM2_simplified.geojson",
        "count": 199,
        "year": "2020",
        "source": "OCHA ROCCA",
        "license": "Creative Commons Attribution 3.0 Intergovernmental Organisations (CC BY 3.0 IGO)",
        "source_url": "https://data.humdata.org/dataset/ubbekistan-update",
    },
}

MAPSPAM_URL = (
    "https://raw.githubusercontent.com/Sherzoddd2002/osh-agriculture-ai-global/"
    f"{MAPSPAM_COMMIT}/docs/data/mapspam/global/UZB.json.gz"
)

SIAT = {
    "whea": {
        "name": "Bug‘doy",
        "production_code": "1.03.03.0010",
        "production_url": "https://api.siat.stat.uz/media/uploads/sdmx/sdmx_data_1458.json",
        "production_page": "https://siat.stat.uz/data/1458/?lang=en",
        "area_code": "1.03.03.0084",
        "area_unit": "hectare",
        "area_url": "https://api.siat.stat.uz/media/uploads/sdmx/sdmx_data_2761.json",
        "area_page": "https://siat.stat.uz/data/2761/?lang=en",
        "max_yield": 30.0,
        "allow_partial": True,
    },
    "pota": {
        "name": "Kartoshka",
        "production_code": "1.03.03.0031",
        "production_url": "https://api.siat.stat.uz/media/uploads/sdmx/sdmx_data_323.json",
        "production_page": "https://siat.stat.uz/data/323/?lang=en",
        "area_code": "1.03.03.0070",
        "area_unit": "hectares",
        "area_url": "https://api.siat.stat.uz/media/uploads/sdmx/sdmx_data_2040.json",
        "area_page": "https://siat.stat.uz/data/2040/?lang=en",
        "max_yield": 200.0,
        "allow_partial": False,
    },
    "cott": {
        "name": "Paxta (xom paxta)",
        "production_code": "1.03.03.0073",
        "production_url": "https://api.siat.stat.uz/media/uploads/sdmx/sdmx_data_2389.json",
        "production_page": "https://siat.stat.uz/data/2389/?lang=en",
        "area_code": "1.03.03.0069",
        "area_unit": "hectares",
        "area_url": "https://api.siat.stat.uz/media/uploads/sdmx/sdmx_data_2039.json",
        "area_page": "https://siat.stat.uz/data/2039/?lang=en",
        "max_yield": 20.0,
        "allow_partial": False,
    },
}


def fetch_bytes(url: str, timeout: int = 90) -> bytes:
    request = Request(url, headers={"User-Agent": "OSH-AgroAI-Uzbekistan/1.0 (public data build)"})
    with urlopen(request, timeout=timeout) as response:
        data = response.read()
        if response.status != 200 or not data:
            raise RuntimeError(f"HTTP {response.status} or empty response: {url}")
        return data


def fetch_json(url: str) -> object:
    return json.loads(fetch_bytes(url).decode("utf-8"))


def write_json(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, ensure_ascii=False, separators=(",", ":"), allow_nan=False),
        encoding="utf-8",
    )


def build_boundaries(output: Path) -> dict:
    results = {}
    boundary_dir = output / "boundaries"
    boundary_dir.mkdir(parents=True, exist_ok=True)

    for level, config in BOUNDARIES.items():
        payload = json.loads(fetch_bytes(config["url"]).decode("utf-8"))
        if payload.get("type") != "FeatureCollection":
            raise ValueError(f"UZB {level}: GeoJSON FeatureCollection emas")
        features = payload.get("features")
        if not isinstance(features, list) or len(features) != config["count"]:
            actual = len(features) if isinstance(features, list) else "not-a-list"
            raise ValueError(f"UZB {level}: {config['count']} feature kutilgan, topildi: {actual}")

        identifiers = set()
        for index, feature in enumerate(features):
            if not isinstance(feature, dict) or not isinstance(feature.get("geometry"), dict):
                raise ValueError(f"UZB {level}: {index}-feature geometriyasi yo‘q")
            if feature["geometry"].get("type") not in {"Polygon", "MultiPolygon"}:
                raise ValueError(f"UZB {level}: qo‘llab-quvvatlanmaydigan geometriya")
            props = feature.setdefault("properties", {})
            shape_id = str(props.get("shapeID") or "").strip()
            shape_name = str(props.get("shapeName") or "").strip()
            if not shape_id or not shape_name or shape_id in identifiers:
                raise ValueError(f"UZB {level}: shapeID/name yo‘q yoki takroriy: {shape_id!r}")
            identifiers.add(shape_id)
            props["shapeType"] = level
            props["countryISO3"] = "UZB"

        if len(identifiers) != config["count"]:
            raise ValueError(f"UZB {level}: takrorlanmagan ID soni mos emas")

        metadata = {
            "country_iso3": "UZB",
            "admin_level": level,
            "boundary_year": config["year"],
            "source": config["source"],
            "license": config["license"],
            "source_url": config["source_url"],
            "provider": "geoBoundaries",
            "provider_commit": BOUNDARY_COMMIT,
            "simplified": True,
        }
        payload["metadata"] = metadata
        path = boundary_dir / f"UZB_{level}.geojson"
        write_json(path, payload)
        results[level] = {
            "file": f"boundaries/{path.name}",
            "feature_count": len(features),
            **metadata,
        }
        print(f"PASS UZB {level}: {len(features)} polygon · vintage {config['year']}")

    return results


def build_mapspam(output: Path) -> dict:
    data = fetch_bytes(MAPSPAM_URL)
    payload = json.loads(gzip.decompress(data).decode("utf-8"))
    if (
        payload.get("country_iso3") != "UZB"
        or payload.get("dataset_id") != "mapspam-2020-v2r2"
        or payload.get("source_year") != 2020
        or payload.get("license") != "CC BY-SA 4.0"
        or payload.get("source_url") != "https://doi.org/10.7910/DVN/SWPENT"
    ):
        raise ValueError("UZB MAPSPAM paketi identity/license/source tekshiruvidan o‘tmadi")

    levels = payload.get("levels") or {}
    counts = {"ADM1": 14, "ADM2": 199}
    summary_rows = 0
    for level, expected in counts.items():
        areas = (levels.get(level) or {}).get("areas") or {}
        if len(areas) != expected:
            raise ValueError(f"UZB MAPSPAM {level}: {expected} kutilgan, {len(areas)} topildi")
        for area_id, area in areas.items():
            crops = area.get("crops") or {}
            if len(crops) != 46:
                raise ValueError(f"UZB {level}/{area_id}: 46 ekin qatori talab qilinadi")
            for code, row in crops.items():
                cells = row.get("valid_cells")
                yld = row.get("yield_t_ha")
                status = row.get("spatial_status")
                if isinstance(cells, bool) or not isinstance(cells, (int, float)) or cells < 0:
                    raise ValueError(f"UZB {level}/{area_id}/{code}: valid_cells noto‘g‘ri")
                if yld is not None and (
                    isinstance(yld, bool) or not isinstance(yld, (int, float))
                    or not math.isfinite(float(yld)) or yld < 0
                ):
                    raise ValueError(f"UZB {level}/{area_id}/{code}: yield noto‘g‘ri")
                if status == "NO_RASTER_CELLS":
                    if cells != 0 or yld is not None:
                        raise ValueError("NO_RASTER_CELLS null/zero qoidasi buzilgan")
                elif status == "ESTIMATED":
                    if cells <= 0 or yld is None:
                        raise ValueError("ESTIMATED yozuvda valid_cells/yield yetishmaydi")
                else:
                    raise ValueError(f"Unknown spatial_status: {status!r}")
            summary_rows += len(crops)

    adm1_ids = set((levels["ADM1"]["areas"] or {}).keys())
    parent_ids = {
        str(row.get("parent_admin_id") or "").strip()
        for row in (levels["ADM2"]["areas"] or {}).values()
    }
    if parent_ids != adm1_ids:
        raise ValueError("UZB ADM2 parent ID to‘plami 14 ta ADM1 bilan mos emas")

    target = output / "mapspam" / "UZB.json.gz"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(data)
    print(f"PASS MAPSPAM UZB: ADM1=14 · ADM2=199 · crops=46 · rows={summary_rows}")
    return {
        "file": "mapspam/UZB.json.gz",
        "source_year": 2020,
        "country_iso3": "UZB",
        "province_count": 14,
        "district_count": 199,
        "crop_count": 46,
        "summary_rows": summary_rows,
        "license": "CC BY-SA 4.0",
        "source_url": "https://doi.org/10.7910/DVN/SWPENT",
        "compressed_bytes": len(data),
    }


def siat_document(payload: object, code: str, unit: str) -> dict:
    if isinstance(payload, list) and len(payload) == 1:
        payload = payload[0]
    if not isinstance(payload, dict):
        raise ValueError(f"SIAT {code}: kutilgan data object topilmadi")
    metadata = payload.get("metadata") or []
    values = {row.get("name_en"): row.get("value_en") for row in metadata if isinstance(row, dict)}
    if values.get("Indicator identification number (code)") != code:
        raise ValueError(f"SIAT {code} indicator code mismatch: {values.get('Indicator identification number (code)')!r}")
    if values.get("Unit of measurement") != unit:
        raise ValueError(f"SIAT {code} unit mismatch: {values.get('Unit of measurement')!r}")
    rows = payload.get("data")
    if not isinstance(rows, list) or not rows:
        raise ValueError(f"SIAT {code}: data qatori bo‘sh")
    return {"metadata": values, "records": rows}


def build_siat_crop(output: Path, crop_code: str, definition: dict) -> dict:
    production_doc = siat_document(
        fetch_json(definition["production_url"]),
        definition["production_code"],
        "thousand tons",
    )
    area_doc = siat_document(
        fetch_json(definition["area_url"]),
        definition["area_code"],
        definition["area_unit"],
    )
    production = {
        str(row.get("Code")): row for row in production_doc["records"]
        if isinstance(row, dict) and row.get("Code") is not None
    }
    area = {
        str(row.get("Code")): row for row in area_doc["records"]
        if isinstance(row, dict) and row.get("Code") is not None
    }
    regions = []
    for code in sorted(set(production) & set(area)):
        if code in {"1700", "1726"}:
            continue
        p_row, a_row = production[code], area[code]
        name = " ".join(str(p_row.get("Klassifikator") or "").split())
        area_name = " ".join(str(a_row.get("Klassifikator") or "").split())
        if not name or name != area_name:
            raise ValueError(f"SIAT {crop_code}: {code} hudud nomlari mos emas: {name!r}/{area_name!r}")
        records = []
        for year in YEARS:
            p_value, a_value = p_row.get(str(year)), a_row.get(str(year))
            if p_value is None or a_value is None:
                if definition["allow_partial"]:
                    continue
                raise ValueError(f"SIAT {crop_code}: {name} {year} qatori yetishmaydi")
            production_thousand_t, area_ha = float(p_value), float(a_value)
            if production_thousand_t <= 0 or area_ha <= 0:
                if definition["allow_partial"]:
                    continue
                raise ValueError(f"SIAT {crop_code}: {name} {year} production/area musbat emas")
            production_t = production_thousand_t * 1000.0
            yield_t_ha = production_t / area_ha
            if not 0 < yield_t_ha < definition["max_yield"]:
                raise ValueError(f"SIAT {crop_code}: {name} {year} yield plausibility check failed: {yield_t_ha}")
            records.append({
                "year": year,
                "yield": round(yield_t_ha, 6),
                "production_t": round(production_t, 3),
                "sown_area_ha": round(area_ha, 3),
            })
        min_years = 12 if definition["allow_partial"] else len(YEARS)
        if len(records) >= min_years:
            regions.append({"admin_code": code, "name_uz": name, "records": records})

    if len(regions) != 13:
        raise ValueError(f"SIAT {crop_code}: 13 qishloq xo‘jaligi viloyati kutilgan, {len(regions)} topildi")
    for region in regions:
        years = [row["year"] for row in region["records"]]
        if len(years) != len(set(years)):
            raise ValueError(f"SIAT {crop_code}: {region['name_uz']} takroriy yil")
        if not definition["allow_partial"] and years != list(YEARS):
            raise ValueError(f"SIAT {crop_code}: {region['name_uz']} 2010–2024 qatori to‘liq emas")

    payload = {
        "country_iso3": "UZB",
        "admin_level": "ADM1",
        "crop_code": crop_code,
        "crop_name_uz": definition["name"],
        "unit": "tonnes per planted hectare",
        "years": [YEARS[0], YEARS[-1]],
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "method": "official production (thousand tonnes) * 1000 / official sown area (hectares)",
        "sources": [
            {
                "indicator_code": definition["production_code"],
                "name": "Crop production in all categories of farms",
                "unit": "thousand tons",
                "url": definition["production_page"],
                "raw_url": definition["production_url"],
                "updated": production_doc["metadata"].get("Last modified date"),
            },
            {
                "indicator_code": definition["area_code"],
                "name": "Crop sown area in all categories of farms",
                "unit": definition["area_unit"],
                "url": definition["area_page"],
                "raw_url": definition["area_url"],
                "updated": area_doc["metadata"].get("Last modified date"),
            },
        ],
        "license": "CC BY 4.0",
        "geographic_coverage": "13 agricultural ADM1 regions; Tashkent city excluded",
        "district_yield_available": False,
        "regions": sorted(regions, key=lambda row: row["name_uz"]),
    }
    path = output / "official-yield" / f"UZB_ADM1_{crop_code.upper()}_2010_2024.json"
    write_json(path, payload)
    print(f"PASS SIAT {crop_code}: 13 viloyat · {sum(len(r['records']) for r in regions)} yillik yozuv")
    return {
        "file": f"official-yield/{path.name}",
        "crop_code": crop_code,
        "crop_name_uz": definition["name"],
        "regions": len(regions),
        "yearly_records": sum(len(r["records"]) for r in regions),
        "license": "CC BY 4.0",
        "district_yield_available": False,
        "sources": payload["sources"],
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=Path("site/data"))
    args = parser.parse_args()
    output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=True)

    boundaries = build_boundaries(output)
    mapspam = build_mapspam(output)
    siat_status = {}
    for crop_code, definition in SIAT.items():
        try:
            siat_status[crop_code] = build_siat_crop(output, crop_code, definition)
        except Exception as exc:
            # SIAT API is external. The site can still deploy with exact district
            # MAPSPAM data and user-provided district CSV; it must not fabricate a series.
            siat_status[crop_code] = {
                "status": "UNAVAILABLE",
                "reason": f"{type(exc).__name__}: {exc}",
                "district_yield_available": False,
            }
            print(f"WARN SIAT {crop_code}: automatic official series not published: {exc}")

    manifest = {
        "product": "OSH AgroAI Uzbekistan",
        "country_iso3": "UZB",
        "built_at_utc": datetime.now(timezone.utc).isoformat(),
        "boundaries": boundaries,
        "mapspam": mapspam,
        "siat": siat_status,
        "weather": {
            "provider": "Open-Meteo",
            "archive_model": "ERA5-Land",
            "scope": "Representative point for selected area; not polygon zonal mean",
        },
    }
    write_json(output / "manifest.json", manifest)
    print("PASS UZB public data bundle created:", output)
    print("SIAT status:", json.dumps({k: v.get("status", "AVAILABLE") for k, v in siat_status.items()}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
