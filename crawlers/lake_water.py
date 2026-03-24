#!/usr/bin/env python3
"""
lake_water.py — Crawl lake/reservoir level data from Thuy Loi Vietnam.

Source: http://e15.thuyloivietnam.vn/CanhBaoSoLieu/ATCBDTHo
Output: lake.csv

Usage:
    python crawlers/lake_water.py                          # today → today
    python crawlers/lake_water.py --start 2025-10-07       # custom start
    python crawlers/lake_water.py --start 2025-10-07 --end 2025-11-01
    python crawlers/lake_water.py --out /path/to/lake.csv
"""

import argparse
import csv
import re
import sys
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path
from urllib.parse import parse_qs, urlencode, urlparse, urlunparse

import requests

# Allow running as a script from any directory
sys.path.insert(0, str(Path(__file__).parent))
from config import LAKE_API_BASE, LAKE_FIELDS, LAKE_POSITION_MAP

GMT7 = timezone(timedelta(hours=7))


# ── Helpers ──────────────────────────────────────────────────────────────────

def ms_epoch_to_gmt7(epoch_string: str) -> str:
    """Convert a Microsoft JSON date string (e.g. '/Date(1762483534410)/') to GMT+7."""
    try:
        match = re.search(r"(\d+)", epoch_string)
        if not match:
            return "Invalid Format"
        dt = datetime.fromtimestamp(int(match.group(1)) / 1000.0, GMT7)
        return dt.strftime("%Y-%m-%d %H:%M:%S %Z")
    except Exception as e:
        print(f"  [WARN] timestamp conversion failed for '{epoch_string}': {e}")
        return "Conversion Error"


def fetch_date(date_str: str, base_url: str) -> list | None:
    """Fetch lake data for a single date. Returns list of records or None on error."""
    parsed = urlparse(base_url)
    params = parse_qs(parsed.query)
    params["time"] = [f"{date_str} 00:00:00,000"]
    url = urlunparse((
        parsed.scheme, parsed.netloc, parsed.path,
        parsed.params, urlencode(params, doseq=True), parsed.fragment,
    ))
    try:
        r = requests.get(url, timeout=30)
        r.raise_for_status()
        return r.json()
    except requests.exceptions.RequestException as e:
        print(f"  [WARN] network error for {date_str}: {e}")
    except ValueError:
        print(f"  [WARN] non-JSON response for {date_str}")
    return None


# ── Main ─────────────────────────────────────────────────────────────────────

def crawl(start_date: str, end_date: str, out_path: Path) -> None:
    start = datetime.strptime(start_date, "%Y-%m-%d").date()
    end   = datetime.strptime(end_date,   "%Y-%m-%d").date()
    print(f"Fetching lake data: {start} → {end}")

    all_rows = []
    current = start
    while current <= end:
        ds = current.strftime("%Y-%m-%d")
        records = fetch_date(ds, LAKE_API_BASE)
        if records:
            print(f"  {ds}: {len(records)} records")
            for rec in records:
                try:
                    code = rec.get("LakeCode")
                    pos  = LAKE_POSITION_MAP.get(code, {})
                    left = top = canvas = None
                    if pos:
                        left, top = pos.get("pos", ",").split(",")
                        canvas = pos.get("canvas")
                    all_rows.append({
                        "Date":   ds,
                        "LakeName":    rec.get("LakeName"),
                        "LakeCode":    code,
                        "BasinName":   rec.get("BasinName"),
                        "ProvinceName": rec.get("ProvinceName"),
                        "TdMucNuoc (Mực nước - m)":   rec.get("TdMucNuoc"),
                        "TdDungTich (Dung tích - m3)": rec.get("TdDungTich"),
                        "TkDungTich (Dung tích thiết kế - m3)": rec.get("TkDungTich"),
                        "TiLeDungTichTdSoTk (Tỷ lệ dung tích - %)": rec.get("TiLeDungTichTdSoTk"),
                        "QDen (m3/s)": rec.get("QDen"),
                        "QXa (m3/s)":  rec.get("QXa"),
                        "ThoiGianCapNhat (GMT+7)": ms_epoch_to_gmt7(rec.get("ThoiGianCapNhat", "")),
                        "X": rec.get("X"), "Y": rec.get("Y"),
                        "Left": left, "Top": top, "CanvasName": canvas,
                    })
                except Exception as e:
                    print(f"  [WARN] skipping record: {e}")
        else:
            print(f"  {ds}: no data")
        current += timedelta(days=1)
        time.sleep(1)

    if not all_rows:
        print("No data fetched.")
        return

    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=LAKE_FIELDS)
        writer.writeheader()
        writer.writerows(all_rows)
    print(f"\n✓ {len(all_rows)} rows → {out_path}")


def main():
    today = datetime.now(GMT7).date().isoformat()
    parser = argparse.ArgumentParser(description="Crawl lake water levels from Thuy Loi Vietnam")
    parser.add_argument("--start", default="2025-10-07", help="Start date YYYY-MM-DD (default: 2025-10-07)")
    parser.add_argument("--end",   default=today,       help="End date YYYY-MM-DD (default: today)")
    parser.add_argument("--out",   default="lake.csv",  help="Output CSV path (default: lake.csv)")
    args = parser.parse_args()
    crawl(args.start, args.end, Path(args.out))


if __name__ == "__main__":
    main()
