#!/usr/bin/env python3
"""
landslide.py — Crawl landslide/flash flood warnings from NCHMF.

Source: https://luquetsatlo.nchmf.gov.vn/LayerMapBox/getDSCanhbaoSLLQ
Output: landslide.csv

Usage:
    # Historical mode: crawl hourly over a time window
    python crawlers/landslide.py --mode historical --start "2025-11-06 00:00" --end "2025-11-10 00:00"

    # Refresh mode: fetch only the current hour (for dashboards)
    python crawlers/landslide.py --mode refresh

    # Override output path
    python crawlers/landslide.py --mode refresh --out data/landslide.csv
"""

import argparse
import json
import sys
import time
from datetime import datetime, timedelta
from pathlib import Path

import pandas as pd
import pytz
import requests

sys.path.insert(0, str(Path(__file__).parent))
from config import (
    LANDSLIDE_ENDPOINT,
    LANDSLIDE_SEVERITY_RANK,
    LANDSLIDE_SOGIO_DU_BAO,
    LANDSLIDE_TARGET_PROVINCES,
)

VN_TZ = pytz.timezone("Asia/Ho_Chi_Minh")


# ── Helpers ──────────────────────────────────────────────────────────────────

def severity_score(row: dict) -> int:
    s1 = LANDSLIDE_SEVERITY_RANK.get(str(row.get("nguycosatlo", "")).strip(), 0)
    s2 = LANDSLIDE_SEVERITY_RANK.get(str(row.get("nguycoluquet", "")).strip(), 0)
    return max(s1, s2)


def post_with_retries(url: str, data: dict, max_retries: int = 3, timeout: int = 45):
    delay = 1.5
    for attempt in range(1, max_retries + 1):
        try:
            r = requests.post(url, data=data, timeout=timeout)
            if r.status_code == 200:
                return r
            raise requests.HTTPError(f"HTTP {r.status_code}")
        except Exception as e:
            if attempt == max_retries:
                raise
            print(f"  [WARN] attempt {attempt} failed: {e}. Retrying in {delay:.1f}s")
            time.sleep(delay)
            delay *= 2


def fetch_hour(dt: datetime) -> list:
    """Fetch landslide data for a single hour. Returns list of filtered records."""
    date_str = dt.strftime("%Y-%m-%d %H:%M:%S")
    payload = {"sogiodubao": LANDSLIDE_SOGIO_DU_BAO, "date": date_str}
    try:
        resp = post_with_retries(LANDSLIDE_ENDPOINT, data=payload)
        try:
            data = resp.json()
        except Exception:
            data = json.loads(resp.text)
        if not isinstance(data, list):
            return []
        results = []
        for row in data:
            prov = str(row.get("provinceName_2cap", "")).strip()
            commune = str(row.get("commune_name_2cap", "")).strip()
            if commune.startswith("P. "):
                commune = commune[3:].strip()
            results.append({
                "time": date_str,
                "commune_id_2cap":   row.get("commune_id_2cap"),
                "commune_name_2cap": commune,
                "provinceName_2cap": prov,
                "nguycosatlo":  row.get("nguycosatlo"),
                "nguycoluquet": row.get("nguycoluquet"),
            })
        return results
    except Exception as e:
        print(f"  [WARN] {date_str}: {e}")
        return []


def deduplicate(records: list) -> pd.DataFrame:
    """Keep highest-severity record per (time, commune_id_2cap)."""
    df = pd.DataFrame(records)
    if df.empty:
        return df
    cols = ["time", "commune_id_2cap", "commune_name_2cap",
            "provinceName_2cap", "nguycosatlo", "nguycoluquet"]
    for c in cols:
        if c not in df.columns:
            df[c] = None
    df = df[cols].dropna(subset=["commune_id_2cap", "time"]).copy()
    df["_sev"] = df.apply(severity_score, axis=1)
    dedup = (
        df.sort_values(["time", "commune_id_2cap"])
          .groupby(["time", "commune_id_2cap"], as_index=False, group_keys=False)
          .apply(lambda g: g.loc[g["_sev"].idxmax()])
          .reset_index(drop=True)
    )
    return dedup.drop(columns=["_sev"], errors="ignore")


# ── Modes ─────────────────────────────────────────────────────────────────────

def run_historical(start_str: str, end_str: str, out_path: Path) -> None:
    """Crawl hourly over a historical window and save to CSV."""
    start = VN_TZ.localize(datetime.strptime(start_str, "%Y-%m-%d %H:%M"))
    end   = VN_TZ.localize(datetime.strptime(end_str,   "%Y-%m-%d %H:%M"))

    hours = []
    cur = start.replace(minute=0, second=0, microsecond=0)
    while cur <= end:
        hours.append(cur)
        cur += timedelta(hours=1)

    print(f"Historical mode: {start_str} → {end_str} ({len(hours)} hours)")

    records = []
    for dt in hours:
        batch = fetch_hour(dt)
        # filter provinces
        batch = [r for r in batch if r["provinceName_2cap"] in LANDSLIDE_TARGET_PROVINCES]
        records.extend(batch)
        time.sleep(0.3)

    print(f"Fetched {len(records)} raw records.")
    df = deduplicate(records)
    _save(df, out_path)


def run_refresh(out_path: Path) -> None:
    """Fetch current-hour data only (overwrite mode for dashboards)."""
    now = datetime.now(VN_TZ).replace(minute=0, second=0, microsecond=0)
    print(f"Refresh mode: fetching {now.strftime('%Y-%m-%d %H:%M')}")

    records = fetch_hour(now)
    # No province filter in refresh — return everything
    print(f"Found {len(records)} active records.")
    df = deduplicate(records)
    _save(df, out_path)


def _save(df: pd.DataFrame, out_path: Path) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    if df.empty:
        print("No data to save.")
        df = pd.DataFrame(columns=[
            "time", "commune_id_2cap", "commune_name_2cap",
            "provinceName_2cap", "nguycosatlo", "nguycoluquet",
        ])
    df.sort_values(["provinceName_2cap", "commune_name_2cap"], inplace=True)
    df.to_csv(out_path, index=False, encoding="utf-8-sig")
    print(f"✓ {len(df)} rows → {out_path}")


# ── CLI ───────────────────────────────────────────────────────────────────────

def main():
    now_vn = datetime.now(VN_TZ)
    parser = argparse.ArgumentParser(description="Crawl landslide/flash flood warnings from NCHMF")
    parser.add_argument("--mode",  choices=["historical", "refresh"], default="refresh",
                        help="'historical' for a time window, 'refresh' for current hour (default: refresh)")
    parser.add_argument("--start", default="2025-11-06 00:00",
                        help="Start datetime 'YYYY-MM-DD HH:MM' (historical mode only)")
    parser.add_argument("--end",
                        default=now_vn.replace(minute=0, second=0, microsecond=0).strftime("%Y-%m-%d %H:%M"),
                        help="End datetime 'YYYY-MM-DD HH:MM' (historical mode only, default: now)")
    parser.add_argument("--out",   default="landslide.csv", help="Output CSV path (default: landslide.csv)")
    args = parser.parse_args()

    if args.mode == "historical":
        run_historical(args.start, args.end, Path(args.out))
    else:
        run_refresh(Path(args.out))


if __name__ == "__main__":
    main()
