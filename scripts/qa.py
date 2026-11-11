#!/usr/bin/env python3
"""Release checks for the OSH AgroAI Uzbekistan GitHub Pages bundle."""
from __future__ import annotations

import argparse
import gzip
import json
import math
from pathlib import Path


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--site", type=Path, default=Path("site"))
    parser.add_argument("--require-modis", action="store_true")
    args = parser.parse_args()
    root = args.site.resolve()

    required = [
        root / "index.html",
        root / "app.js",
        root / "styles.css",
        root / "data" / "manifest.json",
        root / "data" / "boundaries" / "UZB_ADM1.geojson",
        root / "data" / "boundaries" / "UZB_ADM2.geojson",
        root / "data" / "mapspam" / "UZB.json.gz",
        root / "data" / "templates" / "district-yield-template.csv",
    ]
    missing = [str(path.relative_to(root)) for path in required if not path.is_file()]
    if missing:
        raise SystemExit("FAIL missing site files: " + ", ".join(missing))

    html = (root / "index.html").read_text(encoding="utf-8")
    js = (root / "app.js").read_text(encoding="utf-8")
    if 'id="map"' not in html or 'id="run-forecast"' not in html:
        raise SystemExit("FAIL homepage does not contain map and AI Predict controls")
    if "fly.dev" in html.lower() or "DATABASE_URL" in html or "api_key" in html.lower():
        raise SystemExit("FAIL public static page contains private backend configuration")
    for required_marker in ("NO_RASTER_CELLS", "Persistence", "ERA5-Land", "UZB"):
        if required_marker not in js:
            raise SystemExit(f"FAIL app.js missing required marker: {required_marker}")
    if "aligned.length<12" not in js or "for(let i=8;i<aligned.length;i++)" not in js or "result.oof.length" not in js:
        raise SystemExit("FAIL AI model minimum-history or OOF reporting guard")
    if "Kamida 12 ta hosildorlik+iqlim mavsumi" not in html or "kamida 80%" not in html:
        raise SystemExit("FAIL AI Predict page does not disclose the 12-year and 80% climate coverage minimum")
    for marker in ("3 409 / 9 154", "37,2%", "585", "647", "1992–2024", "22.03.2025–16.10.2025", "DATA AUDIT"):
        if marker not in html:
            raise SystemExit(f"FAIL public data coverage panel missing: {marker}")
    if "FAOSTAT QCL · 1961–2024" in html or "1961–2024 · UZB" in html:
        raise SystemExit("FAIL Uzbekistan FAOSTAT card must show the exported UZB range, not the global archive range")
    print("PASS AI model: 12-year aligned history, expanding-window OOF and test-count reporting")
    for marker in ("function getDistrictDemoSeries()", "DEMO PROKSI", "demoProxy.baseYield"):
        if marker not in js:
            raise SystemExit(f"FAIL district demo proxy missing required marker: {marker}")
    if "OOF/MAE aniqlik ko‘rsatkichlari va ishonch oralig‘i ko‘rsatilmaydi" not in js:
        raise SystemExit("FAIL district demo proxy must suppress unvalidated accuracy metrics")
    print("PASS district demo proxy: MAPSPAM 2020 baseline + parent-region SIAT trend; no false OOF accuracy")
    if "return {lat:center.lat,lng:center.lng}" not in js:
        raise SystemExit("FAIL selected map center must expose lng for ERA5-Land and NASA POWER")
    for marker in ("function fetchNasaPowerSolar(", "ALLSKY_SFC_SW_DWN", "power.larc.nasa.gov/api/temporal/daily/point", "nasaSolarUsed"):
        if marker not in js:
            raise SystemExit(f"FAIL NASA POWER integration marker missing: {marker}")
    if "NASA POWER" not in html or "MOD13Q1" not in html:
        raise SystemExit("FAIL NASA data provenance cards are missing")
    print("PASS NASA POWER: daily solar radiation feature and source provenance; coordinates aligned")
    if "trainX.push(makeFeatures(aligned,j,useNasaSolar,useModis,useEt0))" not in js:
        raise SystemExit("FAIL OOF training rows must use the same NASA feature schema as validation rows")
    print("PASS Ridge OOF: training and validation feature dimensions match")

    for marker in (
        "function summarizeClimateSeason(",
        "function fetchHistoricalDaily(",
        'for(const model of ["era5_land","era5"])',
        "if(useEt0)features.push",
        "ET₀ barcha mos mavsumlarda",
    ):
        if marker not in js:
            raise SystemExit(f"FAIL historical climate robustness marker missing: {marker}")
    if "ERA5-Land/ERA5 bilan kamida 12 ta mavsum" not in js:
        raise SystemExit("FAIL climate alignment guard must disclose both primary and fallback sources")
    print("PASS historical climate: 5-year API chunks, ERA5-Land + ERA5 fallback, ET0 optional, 80% temp/rain gate")

    template = (root / "data" / "templates" / "district-yield-template.csv").read_text(encoding="utf-8").splitlines()
    if not template or template[0].strip().lower() != "admin_name,crop_code,year,yield_t_ha":
        raise SystemExit("FAIL district CSV template columns")
    print("PASS district CSV template: location and crop provenance columns included")

    manifest = read_json(root / "data" / "manifest.json")
    if manifest.get("country_iso3") != "UZB":
        raise SystemExit("FAIL data manifest is not Uzbekistan-only")

    for level, expected in (("ADM1", 14), ("ADM2", 199)):
        path = root / "data" / "boundaries" / f"UZB_{level}.geojson"
        payload = read_json(path)
        features = payload.get("features") or []
        ids = {
            str((feature.get("properties") or {}).get("shapeID") or "").strip()
            for feature in features
        }
        if payload.get("type") != "FeatureCollection" or len(features) != expected or len(ids) != expected or "" in ids:
            raise SystemExit(f"FAIL boundary QA {level}: expected {expected} unique features")
        metadata = payload.get("metadata") or {}
        if metadata.get("country_iso3") != "UZB" or metadata.get("admin_level") != level:
            raise SystemExit(f"FAIL boundary metadata {level}")
        print(f"PASS {level}: {expected} unique administrative features")

    with gzip.open(root / "data" / "mapspam" / "UZB.json.gz", "rt", encoding="utf-8") as stream:
        mapspam = json.load(stream)
    if (
        mapspam.get("country_iso3") != "UZB"
        or mapspam.get("dataset_id") != "mapspam-2020-v2r2"
        or mapspam.get("source_year") != 2020
        or mapspam.get("license") != "CC BY-SA 4.0"
    ):
        raise SystemExit("FAIL MAPSPAM identity/license")
    levels = mapspam.get("levels") or {}
    boundary_id_sets = {}
    for level, expected in (("ADM1", 14), ("ADM2", 199)):
        areas = (levels.get(level) or {}).get("areas") or {}
        if len(areas) != expected:
            raise SystemExit(f"FAIL MAPSPAM {level}: expected {expected}, got {len(areas)}")
        for area_id, area in areas.items():
            if len(area.get("crops") or {}) != 46:
                raise SystemExit(f"FAIL MAPSPAM crop count: {level}/{area_id}")
        boundary = read_json(root / "data" / "boundaries" / f"UZB_{level}.geojson")
        boundary_ids = {
            str((feature.get("properties") or {}).get("shapeID") or "").strip()
            for feature in (boundary.get("features") or [])
        }
        mapspam_ids = set(areas)
        if boundary_ids != mapspam_ids:
            raise SystemExit(
                f"FAIL {level} boundary/MAPSPAM ID mismatch: "
                f"boundary-only={len(boundary_ids - mapspam_ids)}, "
                f"MAPSPAM-only={len(mapspam_ids - boundary_ids)}"
            )
        boundary_id_sets[level] = boundary_ids
        print(f"PASS {level}: boundary IDs and MAPSPAM IDs match {expected}/{expected}")

    district_parents = {
        str(area.get("parent_admin_id") or "").strip()
        for area in (levels["ADM2"]["areas"] or {}).values()
    }
    if district_parents != boundary_id_sets["ADM1"]:
        raise SystemExit("FAIL MAPSPAM ADM2 parent IDs do not match the 14 ADM1 boundary IDs")

    adm2_areas = levels["ADM2"]["areas"]
    adm2_combinations = sum(len(area.get("crops") or {}) for area in adm2_areas.values())
    adm2_valid = sum(
        1 for area in adm2_areas.values()
        for crop in (area.get("crops") or {}).values()
        if crop.get("spatial_status") == "ESTIMATED" and crop.get("yield_t_ha") is not None
    )
    districts_without_yield = sum(
        1 for area in adm2_areas.values()
        if not any(
            crop.get("spatial_status") == "ESTIMATED" and crop.get("yield_t_ha") is not None
            for crop in (area.get("crops") or {}).values()
        )
    )
    if (adm2_combinations, adm2_valid, districts_without_yield) != (9154, 3409, 29):
        raise SystemExit(
            "FAIL MAPSPAM published coverage changed: "
            f"combinations={adm2_combinations}, valid={adm2_valid}, "
            f"districts_without_yield={districts_without_yield}"
        )
    print("PASS MAPSPAM ADM2 coverage: 3409/9154 valid district-crop combinations (37.2%); 29 districts have no valid crop raster")
    print("PASS MAPSPAM: UZB · ADM1=14 · ADM2=199 · 46 crops · 2020 reference")

    siat = manifest.get("siat") or {}
    for crop in ("whea", "pota", "cott"):
        item = siat.get(crop) or {}
        if item.get("status") != "UNAVAILABLE":
            file_path = root / "data" / str(item.get("file") or "")
            if not file_path.is_file():
                raise SystemExit(f"FAIL SIAT {crop}: manifest file is missing")
            series = read_json(file_path)
            if series.get("country_iso3") != "UZB" or series.get("admin_level") != "ADM1" or series.get("district_yield_available") is not False:
                raise SystemExit(f"FAIL SIAT {crop}: geography or provenance mismatch")
            regions = series.get("regions") or []
            if len(regions) != 13:
                raise SystemExit(f"FAIL SIAT {crop}: expected 13 agricultural regions")
            minimum_years = 12 if crop == "whea" else 15
            for region in regions:
                years = [row.get("year") for row in (region.get("records") or [])]
                if len(years) < minimum_years or years != sorted(set(years)):
                    raise SystemExit(f"FAIL SIAT {crop}: incomplete/non-monotonic yearly series for {region.get('name_uz')}")
            print(f"PASS SIAT {crop}: 13 ADM1 regions; explicitly not district data")
        else:
            print(f"WARN SIAT {crop}: source unavailable; CSV fallback remains enabled")


    faostat_path = root / "data" / "faostat" / "UZB_QCL.json"
    if faostat_path.is_file():
        faostat = read_json(faostat_path)
        crops = faostat.get("crops") or {}
        if (
            faostat.get("country_iso3") != "UZB"
            or faostat.get("admin_level") != "ADM0"
            or faostat.get("source_code") != "FAOSTAT_QCL"
            or not isinstance(crops, dict)
            or not crops
        ):
            raise SystemExit("FAIL FAOSTAT identity/schema: expected UZB ADM0 FAOSTAT_QCL")
        usable_crops = 0
        total_rows = 0
        for crop_code, crop in crops.items():
            if not isinstance(crop, dict) or crop.get("crop_code") != crop_code:
                raise SystemExit(f"FAIL FAOSTAT crop identity: {crop_code}")
            records = crop.get("records") or []
            years = []
            for row in records:
                try:
                    year = int(row.get("year"))
                except (TypeError, ValueError):
                    raise SystemExit(f"FAIL FAOSTAT invalid year: {crop_code}")
                value = row.get("yield_t_ha")
                if (
                    year < 1961 or year > 2024
                    or not isinstance(value, (int, float))
                    or not math.isfinite(float(value))
                    or float(value) <= 0
                ):
                    raise SystemExit(f"FAIL FAOSTAT invalid yield/year: {crop_code}/{year}")
                years.append(year)
            if years != sorted(set(years)):
                raise SystemExit(f"FAIL FAOSTAT duplicate/non-monotonic years: {crop_code}")
            total_rows += len(records)
            if len(records) >= 12 and 2020 in years:
                usable_crops += 1
        if faostat.get("crop_count") != len(crops):
            raise SystemExit("FAIL FAOSTAT crop_count metadata mismatch")
        if usable_crops == 0:
            raise SystemExit("FAIL FAOSTAT no crop has 12+ rows and a 2020 baseline")
        if (
            faostat.get("year_range") != [1992, 2024]
            or faostat.get("record_count") != 647
            or len(crops) != 21
            or total_rows != 647
            or usable_crops != 20
        ):
            raise SystemExit(
                "FAIL FAOSTAT UZB snapshot: expected 21 crop codes, 647 rows, "
                "1992–2024 range and 20 usable proxy series"
            )
        print(f"PASS FAOSTAT: UZB national ADM0 · {len(crops)} crop codes · {total_rows} annual rows · {usable_crops} usable proxy series")
    else:
        print("INFO FAOSTAT: local UZB export not published yet; SIAT and CSV modes remain available")

    exporter_path = Path("scripts") / "export_faostat_uzb.py"
    exporter = exporter_path.read_text(encoding="utf-8")
    if 'strip().upper()' not in exporter or "if not all_years:" not in exporter:
        raise SystemExit("FAIL FAOSTAT exporter must normalize crop codes case-insensitively and reject empty exports")
    print("PASS FAOSTAT exporter: uppercase crop crosswalk and empty-export guard")

    for marker in ("async function loadFAOSTAT()", "function getFAOSTATProxySeries(", "FAOSTAT MILLIY TREND PROKSISI"):
        if marker not in js:
            raise SystemExit(f"FAIL FAOSTAT integration marker missing: {marker}")
    if 'id="faostat-state"' not in html or 'id="faostat-summary"' not in html:
        raise SystemExit("FAIL FAOSTAT status UI is missing")
    print("PASS FAOSTAT integration: UZB ADM0 national trend is optional and explicitly labelled as proxy")

    modis_path = root / "data" / "modis" / "UZB_ADM2_MOD13Q1.json"
    if args.require_modis and not modis_path.is_file():
        raise SystemExit("FAIL required NASA MODIS district dataset is missing")
    if modis_path.is_file():
        modis = read_json(modis_path)
        areas = modis.get("areas") or {}
        if modis.get("country_iso3") != "UZB" or modis.get("admin_level") != "ADM2" or modis.get("product_id") != "MOD13Q1.061":
            raise SystemExit("FAIL MODIS identity/provenance metadata")
        if len(areas) != 199:
            raise SystemExit(f"FAIL MODIS district coverage: expected 199, got {len(areas)}")
        for area_id, area in areas.items():
            observations = area.get("observations") or []
            dates = [row.get("date") for row in observations]
            if dates != sorted(set(dates)):
                raise SystemExit(f"FAIL MODIS duplicate/non-monotonic dates for {area_id}")
            for row in observations:
                for metric in ("ndvi_mean", "evi_mean", "good_pixel_fraction"):
                    value = row.get(metric)
                    if value is not None and not isinstance(value, (int, float)):
                        raise SystemExit(f"FAIL MODIS non-numeric {metric} for {area_id}")
                fraction = row.get("good_pixel_fraction")
                if fraction is not None and not 0 <= fraction <= 1:
                    raise SystemExit(f"FAIL MODIS quality fraction out of bounds for {area_id}")
        if not modis.get("quality_policy"):
            raise SystemExit("FAIL MODIS quality policy is missing")
        observation_dates = sorted({
            str(row.get("date"))
            for area in areas.values()
            for row in (area.get("observations") or [])
        })
        total_observations = sum(len(area.get("observations") or []) for area in areas.values())
        quality_usable = sum(
            1 for area in areas.values()
            for row in (area.get("observations") or [])
            if row.get("quality_usable")
        )
        if (
            observation_dates != [
                "2025-03-22", "2025-04-07", "2025-04-23", "2025-05-09",
                "2025-05-25", "2025-06-10", "2025-06-26", "2025-07-12",
                "2025-07-28", "2025-08-13", "2025-08-29", "2025-09-14",
                "2025-09-30", "2025-10-16"
            ]
            or total_observations != 2786
            or quality_usable != 2548
        ):
            raise SystemExit(
                "FAIL MODIS snapshot coverage: expected 14 composites, 2786 district rows, "
                "2548 QA-usable observations"
            )
        print(f"PASS NASA MODIS: MOD13Q1.061 · {len(areas)} districts · QA-filtered time series")
    else:
        print("INFO NASA MODIS: no extracted zonal data yet; optional loader stays disabled")

    for marker in ("function getModisSeriesByYear(", "function fetchNasaPowerSolar(", "modisUsed"):
        if marker not in js:
            raise SystemExit(f"FAIL JS data integration marker missing: {marker}")
    if 'id="modis-state"' not in html or "MODIS MOD13Q1" not in html:
        raise SystemExit("FAIL NASA MODIS UI/source provenance is missing")
    print("PASS NASA MODIS UI: district vegetation panel and optional model features")

    print("PASS OSH AgroAI Uzbekistan static release QA")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
