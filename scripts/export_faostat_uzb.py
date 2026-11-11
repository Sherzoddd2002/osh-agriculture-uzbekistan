#!/usr/bin/env python3
"""Export Uzbekistan FAOSTAT QCL yields from the existing local global archive.

Read-only source: osh_agriculture_global.global_crop_statistics.
No credentials or user-uploaded records are exported.
"""
from __future__ import annotations

import argparse
import json
import math
import os
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from sqlalchemy import create_engine, text

DEFAULT_DATABASE_URL = (
    "postgresql+psycopg://osh_global_app@127.0.0.1:5433/osh_agriculture_global"
)
DEFAULT_OUTPUT = Path("data/faostat/UZB_QCL.json")
SOURCE_CODE = "FAOSTAT_QCL"

# Conservative one-to-one mapping from the normalized codes used by the
# central OSH FAOSTAT importer to MAPSPAM's 4-character crop catalogue.
# Composite items (coffee split into Arabica/Robusta, citrus/fruit groups, etc.)
# are intentionally not forced into a single MAPSPAM crop.
FAOSTAT_TO_MAPSPAM = {
    "WHEAT": "whea",
    "MAIZE": "maiz",
    "RICE": "rice",
    "SOYBEAN": "soyb",
    "FAO_44": "barl",
    "FAO_83": "sorg",
    "FAO_108": "ocer",
    "FAO_116": "pota",
    "FAO_122": "swpo",
    "FAO_125": "cass",
    "FAO_137": "yams",
    "FAO_149": "orts",
    "FAO_156": "sugc",
    "FAO_157": "sugb",
    "FAO_176": "bean",
    "FAO_191": "chic",
    "FAO_195": "cowp",
    "FAO_197": "pige",
    "FAO_201": "lent",
    "FAO_211": "opul",
    "FAO_242": "grou",
    "FAO_249": "cnut",
    "FAO_254": "oilp",
    "FAO_267": "sunf",
    "FAO_270": "rape",
    "FAO_289": "sesa",
    "FAO_339": "ooil",
    "FAO_388": "toma",
    "FAO_403": "onio",
    "FAO_463": "vege",
    "FAO_486": "bana",
    "FAO_489": "plnt",
    "FAO_603": "trof",
    "FAO_661": "coco",
    "FAO_667": "teas",
    "FAO_821": "ofib",
    "FAO_826": "toba",
}


def number(value: Any) -> float | None:
    if value is None:
        return None
    try:
        result = float(value)
    except (TypeError, ValueError):
        return None
    return result if math.isfinite(result) else None


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Read-only export of Uzbekistan FAOSTAT QCL crop-yield history."
    )
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--database-url", default=os.environ.get("DATABASE_URL") or DEFAULT_DATABASE_URL)
    args = parser.parse_args()

    engine = create_engine(args.database_url, pool_pre_ping=True, future=True)
    query = text("""
        SELECT
            source_code, source_release, area_m49, country_iso3, area_name,
            item_code, crop_code, crop_name, year,
            harvested_area_ha, production_t, yield_t_ha,
            area_flag, production_flag, yield_flag
        FROM global_crop_statistics
        WHERE source_code = :source_code
          AND country_iso3 = :country_iso3
          AND year BETWEEN 1961 AND 2024
        ORDER BY crop_code, item_code, year
    """)

    try:
        with engine.connect() as connection:
            rows = [dict(row._mapping) for row in connection.execute(
                query, {"source_code": SOURCE_CODE, "country_iso3": "UZB"}
            )]
    finally:
        engine.dispose()

    if not rows:
        raise SystemExit(
            "FAIL: global_crop_statistics jadvalida UZB / FAOSTAT_QCL qatori topilmadi. "
            "PostgreSQL 5433, osh_agriculture_global va pgpass.conf ni tekshiring."
        )

    # Do not merge distinct FAOSTAT items into one crop merely because an
    # upstream normalization mapped them to the same crop_code.
    grouped: dict[str, dict[str, list[dict[str, Any]]]] = defaultdict(lambda: defaultdict(list))
    releases: set[str] = set()
    area_names: set[str] = set()
    area_codes: set[str] = set()

    for raw in rows:
        crop_code = str(raw.get("crop_code") or "").strip().upper()
        item_code = str(raw.get("item_code") or "").strip()
        try:
            year = int(raw.get("year"))
        except (TypeError, ValueError):
            continue
        value = number(raw.get("yield_t_ha"))
        if not crop_code or not item_code or not (1961 <= year <= 2024):
            continue
        if value is None or value <= 0:
            continue

        record = {
            "year": year,
            "yield_t_ha": value,
            "harvested_area_ha": number(raw.get("harvested_area_ha")),
            "production_t": number(raw.get("production_t")),
            "area_flag": raw.get("area_flag"),
            "production_flag": raw.get("production_flag"),
            "yield_flag": raw.get("yield_flag"),
        }
        grouped[crop_code][item_code].append(record)
        if raw.get("source_release"):
            releases.add(str(raw["source_release"]))
        if raw.get("area_name"):
            area_names.add(str(raw["area_name"]))
        if raw.get("area_m49") is not None:
            area_codes.add(str(raw["area_m49"]))

    crops: dict[str, dict[str, Any]] = {}
    ambiguous: list[dict[str, Any]] = []
    too_short: list[dict[str, Any]] = []
    unmapped: list[dict[str, Any]] = []
    mapped_candidates: dict[str, list[tuple[str, str, list[dict[str, Any]]]]] = defaultdict(list)

    for source_crop_code, item_groups in sorted(grouped.items()):
        mapspam_code = FAOSTAT_TO_MAPSPAM.get(source_crop_code)
        if not mapspam_code:
            unmapped.append({
                "source_crop_code": source_crop_code,
                "item_codes": sorted(item_groups),
                "reason": "no conservative one-to-one MAPSPAM crop mapping",
            })
            continue
        if len(item_groups) != 1:
            ambiguous.append({
                "source_crop_code": source_crop_code,
                "mapspam_crop_code": mapspam_code,
                "item_codes": sorted(item_groups),
                "reason": "multiple FAOSTAT item codes share this normalized source crop code",
            })
            continue
        item_code, records = next(iter(item_groups.items()))
        mapped_candidates[mapspam_code].append((source_crop_code, item_code, records))

    for mapspam_code, candidates in sorted(mapped_candidates.items()):
        if len(candidates) != 1:
            ambiguous.append({
                "mapspam_crop_code": mapspam_code,
                "source_crop_codes": sorted(item[0] for item in candidates),
                "reason": "multiple FAOSTAT source crops map to the same MAPSPAM crop",
            })
            continue

        source_crop_code, item_code, records = candidates[0]
        records.sort(key=lambda row: row["year"])
        years = [row["year"] for row in records]
        if len(years) != len(set(years)):
            ambiguous.append({
                "source_crop_code": source_crop_code,
                "mapspam_crop_code": mapspam_code,
                "item_codes": [item_code],
                "reason": "duplicate crop-year records",
            })
            continue
        if len(records) < 12 or 2020 not in years:
            too_short.append({
                "source_crop_code": source_crop_code,
                "mapspam_crop_code": mapspam_code,
                "item_code": item_code,
                "valid_years": len(records),
                "has_2020_reference": 2020 in years,
            })

        crop_name = next(
            (str(row.get("crop_name")) for row in rows
             if str(row.get("crop_code") or "").strip().upper() == source_crop_code
             and str(row.get("item_code") or "").strip() == item_code
             and row.get("crop_name")),
            source_crop_code,
        )
        crop_release = next(
            (str(row.get("source_release")) for row in rows
             if str(row.get("crop_code") or "").strip().upper() == source_crop_code
             and str(row.get("item_code") or "").strip() == item_code
             and row.get("source_release")),
            None,
        )
        crops[mapspam_code] = {
            "crop_code": mapspam_code,
            "source_crop_code": source_crop_code,
            "item_code": item_code,
            "crop_name": crop_name,
            "source_release": crop_release,
            "records": records,
        }

    all_years = [
        record["year"]
        for crop in crops.values()
        for record in crop["records"]
    ]
    valid_count = sum(len(crop["records"]) for crop in crops.values())
    if not all_years:
        observed_codes = sorted({str(row.get("crop_code") or "").strip() for row in rows})
        observed_items = sorted({str(row.get("item_code") or "").strip() for row in rows})
        raise SystemExit(
            "FAIL: UZB FAOSTAT satrlari topildi, lekin crop/item mappingdan so‘ng "
            "yaroqli yield qatori qolmadi. "
            f"Observed crop_code={observed_codes[:30]}; item_code={observed_items[:30]}. "
            "SQL natijalari tekshirildi, bo‘sh JSON yaratilmadi."
        )
    payload = {
        "schema_version": 1,
        "country_iso3": "UZB",
        "country_name": sorted(area_names)[0] if area_names else "Uzbekistan",
        "admin_level": "ADM0",
        "source_code": SOURCE_CODE,
        "source": "FAOSTAT Crops and livestock products (QCL), local OSH global archive",
        "source_releases": sorted(releases),
        "area_m49_codes": sorted(area_codes),
        "year_range": [min(all_years), max(all_years)],
        "crop_count": len(crops),
        "record_count": valid_count,
        "crosswalk": FAOSTAT_TO_MAPSPAM,
        "unmapped_items": unmapped,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "unit": "tonnes per harvested hectare (t/ha)",
        "geography_note": (
            "FAOSTAT series are national ADM0 observations, not province or district observations. "
            "Subnational demo scenarios may scale the 2020 MAPSPAM spatial baseline by this national trend; "
            "they must remain labelled as proxies."
        ),
        "crops": crops,
        "ambiguous_crop_codes": ambiguous,
        "insufficient_history": too_short,
    }

    output = args.output.resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        json.dumps(payload, ensure_ascii=False, separators=(",", ":")),
        encoding="utf-8",
    )
    print(f"[OK] FAOSTAT UZB export: {output}")
    print(f"[OK] source rows read: {len(rows):,}")
    print(f"[OK] unique crop codes exported: {len(crops)}")
    print(f"[OK] valid crop-year yield rows: {valid_count:,}")
    print(f"[OK] year coverage: {payload['year_range'][0]}–{payload['year_range'][1]}")
    print(f"[INFO] ambiguous crop mappings excluded: {len(ambiguous)}")
    print(f"[INFO] unmatched FAOSTAT items kept out of the model: {len(unmapped)}")
    print(f"[INFO] short/no-2020 histories (kept for audit, not used as proxy): {len(too_short)}")
    print("[INFO] available MAPSPAM crop codes:", ", ".join(sorted(crops)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
