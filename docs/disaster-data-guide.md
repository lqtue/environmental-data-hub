# Disaster Data: Sources, Processing & Tools

**Spotlight / VnExpress — Technical Handover Guide**

This guide covers all disaster-related data used across Spotlight dashboards: typhoon tracking, river water levels, lake/reservoir monitoring, flash flood & landslide warnings, flood extent mapping, and rainfall anomaly analysis.

---

## 1. Overview

| Data type | What it answers | Source | Tool / Repo | Update frequency |
|---|---|---|---|---|
| Typhoon real-time track | Where is the storm now, where is it going? | JTWC / JMA | `jtwc_fetch.py` (2025Typhoon) | Every 3–6h during active storm |
| Typhoon historical stats | How often has VN been hit? Which provinces? | IBTrACS (NOAA) | `process_landfall.py` (2025Typhoon) | Once per season |
| River water levels | Are rivers flooding? Which stations exceed alerts? | VNDMS | `water_export_cli.py` (WaterDashboard) | Hourly via GitHub Actions |
| Lake/reservoir storage | How full are reservoirs? Are they releasing water? | Thuy Loi Vietnam | `water_export_cli.py` (WaterDashboard) | Hourly via GitHub Actions |
| Flash flood & landslide warnings | Which communes are at risk right now? | NCHMF | `landslide_export_cli.py` (WaterDashboard) + CentralVN.Landslide | Hourly via GitHub Actions |
| Flood extent mapping | What areas are actually underwater? | VegaCosmos (satellite) + manual | `spotlightvne/floodmap` | Per-event (manual) |
| Rainfall anomaly | Is this storm bringing unusual rain vs normal? | NASA POWER | `fetch_rain.py` (2025Typhoon) | Once per event |

---

## 2. Typhoon Real-Time Track

### 2.1 Primary source: JTWC

The **Joint Typhoon Warning Center** (US Navy/Air Force) publishes Western Pacific tropical cyclone warnings in three formats:

**A. RSS feed** — discover active storms:
```
https://www.metoc.navy.mil/jtwc/rss/jtwc.rss
```

**B. Text warning** — current position + 5-day forecast per storm:
```
https://www.metoc.navy.mil/jtwc/products/wp{NN}{YYYY}.txt
```
Contains: position, max sustained wind (knots), min sea level pressure (mb), and forecast at TAU 12/24/36/48/72/96/120h.

**C. KMZ file** — Google Earth format with wind radii and best track:
```
https://www.metoc.navy.mil/jtwc/products/wp{NN}{YYYY}.kmz
```

**Which to use:**
- Automated/scheduled → text warning (faster, no unzip)
- One-off event coverage → KMZ (wind radii polygons, danger swath)

### 2.2 Fallback: JMA

When JTWC is unavailable, JMA RSMC Tokyo provides current positions only (no forecast):
```
https://www.jma.go.jp/bosai/typhoon/data/targetTc.js
```
This file only exists when storms are active.

### 2.3 Automated fetch: `jtwc_fetch.py`

```bash
pip install requests
python scripts/jtwc_fetch.py
# Output: data/jtwc_active.geojson
```

Pipeline: RSS → discover storms → download text warning → parse position + forecast → GeoJSON. Falls back to JMA on failure.

**GitHub Actions:** `jtwc_fetch.yml` runs every 6h. Trigger manually from the Actions tab for faster updates during active storms.

**Output properties:** `SID`, `NAME`, `USA_WIND` (kt), `USA_PRES` (mb), `track_type` (`current`/`forecast`), `tau` (hours), `category`, `fetched_at`.

### 2.4 Manual KMZ conversion: `kmz_to_geojson.py`

```bash
python scripts/kmz_to_geojson.py path/to/storm.kmz
# Output: data/storm.geojson
```

Extracts 4 feature types (via `feature_type` property):

| `feature_type` | Geometry | What |
|---|---|---|
| `forecast_point` | Point | Position at each TAU |
| `wind_radii` | Polygon | 34/50/64 kt wind extent |
| `best_track_point` | Point | Historical past track |
| `forecast_track` / `danger_swath` | LineString / Polygon | Track line / risk area |

Times are converted to GMT+7 and formatted as Vietnamese (e.g. `T3, 17/3 19:00`).

### 2.5 Wind speed categories

| Knots | km/h | Vietnamese |
|---|---|---|
| < 34 | < 63 | Áp thấp nhiệt đới |
| 34–47 | 63–87 | Bão nhiệt đới |
| 48–63 | 88–117 | Bão nhiệt đới mạnh |
| 64–129 | 118–239 | Bão |
| ≥ 130 | ≥ 241 | Siêu bão |

---

## 3. River Water Levels

### 3.1 Source: VNDMS

**VNDMS** (Cục Quản lý Đê điều và Phòng chống thiên tai) runs a water-level monitoring network across Vietnam.

**Station list endpoint:**
```
GET https://vndms.dmptc.gov.vn/water_level?lv={0,1,2,3}
```
Returns GeoJSON FeatureCollection. The `lv` parameter filters by alert level (0 = normal, 1/2/3 = BĐ1/2/3). Each feature's `popupInfo` HTML contains the station code (`Mã trạm`).

**Station data endpoint:**
```
POST https://vndms.dmc.gov.vn/home/detailRain
     id={station_id}&timeSelect=7&source=Water
```
Returns JSON with:
- `labels`: comma-separated time labels (e.g. `0h \n15/11`)
- `value`: comma-separated water level readings in meters
- `bao_dong1`, `bao_dong2`, `bao_dong3`: alert thresholds
- `gia_tri_lu_lich_su`, `nam_lu_lich_su`: historical flood record

**Important:** VNDMS requires these headers or requests will fail:
```python
headers = {
    "User-Agent": "Mozilla/5.0 ...",
    "Referer": "https://vndms.dmptc.gov.vn/",
    "Origin": "https://vndms.dmptc.gov.vn",
}
```

### 3.2 Currently monitored stations

`config_stations.json` → `"stations"` section lists 16 stations across 6 basins:

| Basin | Stations |
|---|---|
| Sê San | Kon Tum, Kon Plông |
| Hương–Bồ | Phú Ốc, Kim Long |
| Vu Gia–Thu Bồn | Cẩm Lệ, Ái Nghĩa, Hội Khách |
| Trà Khúc | Trà Khúc |
| Kôn–Hà Thanh | Bình Nghi |
| Ba | Củng Sơn, Phú Lâm, An Khê, AyunPa |
| Cái | Ninh Hoà, Đồng Trăng, Tân Mỹ |

**To add a station:** find its numeric ID from the VNDMS website (inspect network requests) and add to `config_stations.json`:
```json
"stations": {
  "71234": {"name": "Station Name", "basin_recode": "Basin Name"}
}
```

### 3.3 Alert classification

Water level is compared against 4 thresholds:

| Level | Vietnamese | Meaning |
|---|---|---|
| 0 | Dưới BĐ1 | Below alert 1 — normal |
| 1 | Trên BĐ1 | Above alert 1 — watch |
| 2 | Trên BĐ2 | Above alert 2 — warning |
| 3 | Trên BĐ3 | Above alert 3 — emergency |
| 4 | Trên lũ lịch sử | Above historical flood record |

---

## 4. Lake/Reservoir Monitoring

### 4.1 Source: Thuy Loi Vietnam

**Thuy Loi Vietnam** (Tổng cục Thủy lợi) publishes daily lake/reservoir data:

```
POST http://e15.thuyloivietnam.vn/CanhBaoSoLieu/ATCBDTHo
     time={YYYY-MM-DD HH:mm:ss,000}&ishothuydien=0
```

**Note:** This endpoint uses HTTP (not HTTPS). Returns JSON array with one object per lake.

Key fields per lake record:

| API field | Meaning |
|---|---|
| `LakeCode` | UUID identifying the lake |
| `TdMucNuoc` | Current water level (m) |
| `TdDungTich` | Current storage volume (m³) |
| `TkDungTich` | Design storage capacity (m³) |
| `TiLeDungTichTdSoTk` | Storage as % of design capacity |
| `QDen` | Inflow (m³/s) |
| `QXa` | Outflow / discharge (m³/s) |
| `MucNuocDangBinhThuong` | Normal operating level (m) |
| `MucNuocDangGiaCuong` | Reinforced (max safe) level (m) |
| `XuThe` | Trend indicator |

### 4.2 Currently monitored lakes

`config_stations.json` → `"lakes"` section lists 22 reservoirs across 7 basins (Sê San, Hương–Bồ, Vu Gia–Thu Bồn, Trà Khúc, Ba, Kôn–Hà Thanh, Cái).

**To add a lake:** find its UUID from the Thuy Loi Vietnam website and add:
```json
"lakes": {
  "UUID-HERE": {"name": "Lake Name", "basin_recode": "Basin", "province_recode": "Province"}
}
```

---

## 5. Flash Flood & Landslide Warnings

### 5.1 Source: NCHMF

**NCHMF** (Trung tâm Dự báo Khí tượng Thủy văn Quốc gia) publishes commune-level risk assessments:

```
POST https://luquetsatlo.nchmf.gov.vn/LayerMapBox/getDSCanhbaoSLLQ
     sogiodubao=6&date={YYYY-MM-DD HH:mm:ss}
```

Returns JSON array, one entry per commune at risk. Each entry has:

| Field | Description |
|---|---|
| `commune_id_2cap` | Commune code |
| `commune_name_2cap` | Commune name |
| `provinceName_2cap` | Province name |
| `nguycosatlo` | Landslide risk: `Rất cao` / `Cao` / `Trung bình` / `Thấp` |
| `nguycoluquet` | Flash flood risk: same scale |

### 5.2 How it works: `landslide_export_cli.py`

```bash
python landslide_export_cli.py
# Output: data/landslide.csv
```

1. Fetches current warning snapshot from NCHMF (rounded to current hour)
2. If a commune appears multiple times, keeps the highest severity
3. Writes to `data/landslide.csv` (overwrite each run — latest state only)

**GitHub Actions:** Runs hourly as part of `main.yml` workflow alongside water data. If new warnings exist, a PR is created and an email sent to the team.

### 5.3 CentralVN.Landslide repo

The `CentralVN.Landslide` repo provides a map visualization focused on Huế and Đà Nẵng communes. Its `list.csv` accumulates hourly snapshots over time (unlike `landslide.csv` in WaterDashboard which only keeps the latest).

`boundary.geojson` contains the commune polygons matched to `commune_id_2cap`.

---

## 6. Flood Extent Mapping

### 6.1 Data sources

Flood area polygons come from two sources depending on the event:

- **VegaCosmos** — Vietnamese satellite imagery provider. After a flood event, they produce classified flood-extent polygons from Sentinel-1 SAR imagery. These are delivered as GeoJSON/shapefiles — there is no public API; data must be requested per event.
- **Manual digitization** — in some cases, flood boundaries are drawn manually from news reports, government announcements, or local observation.

### 6.2 `spotlightvne/floodmap` repo

A deck.gl-based visualization for Northern Vietnam flood events:

| File | Description |
|---|---|
| `flood_area.json` | Flood extent polygons |
| `water.json` | Water gauge data for the event |
| `wards.json` | Ward boundaries (for population impact calculation) |
| `floodmap.html` | Interactive map (deck.gl + TopoJSON) |

**Updating for a new event:** replace `flood_area.json` with the new flood polygons, update `water.json` with the event's water level data, and adjust the map bounds in `floodmap.html`.

---

## 7. Rainfall Anomaly

### 7.1 Source: NASA POWER

**NASA POWER** provides daily precipitation data globally, from 1981 to present. No registration required.

| Endpoint | Returns |
|---|---|
| `GET /api/temporal/daily/point?parameters=PRECTOTCORR&latitude=X&longitude=Y&start=YYYYMMDD&end=YYYYMMDD` | Daily rain (mm) for a point |
| `GET /api/temporal/climatology/point?parameters=PRECTOTCORR&latitude=X&longitude=Y` | 30-year monthly average |

### 7.2 Computing anomaly

For each grid point over Vietnam at 0.5° resolution (~300 points):
1. Fetch daily precipitation for the event period
2. Fetch the 30-year monthly average
3. **Anomaly = actual total − expected total** (positive = wetter than normal)
4. Interpolate from 0.5° to 0.05° resolution, clip to Vietnam boundary

### 7.3 Running `fetch_rain.py`

Edit the date range at the top of the script, place `CountryBoundary.geojson` at repo root, then:

```bash
pip install geopandas pandas numpy requests scipy matplotlib shapely
python scripts/fetch_rain.py
# Output: rain/RainAnomaly.geojson (takes 5–10 min)
```

Run once per event, not on a schedule.

---

## 8. Putting It Together: Typical Workflow

### During an active storm

```
Hourly (auto):     water_export_cli.py    → data/water_data_full_combined.csv
                   landslide_export_cli.py → data/landslide.csv
                   → GitHub Actions creates PR + sends email to team

Every 6h (auto):   jtwc_fetch.py          → data/jtwc_active.geojson
                   → pushed to GitHub, dashboard auto-refreshes

Manual:            Download KMZ            → kmz_to_geojson.py → wind radii
                   Request VegaCosmos data → update floodmap
```

### After the storm (post-event story)

```
1. fetch_rain.py              → rain/RainAnomaly.geojson
2. Download updated IBTrACS   (if season has ended)
3. process_landfall.py        → data/typhoon_landfalls.csv
4. compute_province_metrics.py → data/province_metrics.json
5. Assemble narrative          → story.json + text.md (for FloodViz2/2025typhon2)
```

---

## 9. Known Limitations

### Typhoon data
- **JTWC text parsing is regex-based.** Format changes will break the parser silently. Check `jtwc_active.geojson` at the start of each season.
- **KMZ format is fragile.** Wind radii extraction depends on JTWC's KML structure, which can vary between storms.
- **No automated landfall detection.** `process_landfall.py` runs offline and requires manual IBTrACS download.

### Water & lake data
- **CSV grows unboundedly.** `water_data_full_combined.csv` accumulates hourly readings with no pruning. Consider trimming data older than 30 days each season.
- **Only 16 stations and 22 lakes** are monitored — a curated subset, not the full national network. Adding stations requires manual ID lookup and config editing.
- **VNDMS endpoint is fragile.** Requires spoofed headers (`Referer`, `Origin`). If the site changes authentication, the crawler breaks.
- **Thuy Loi Vietnam uses HTTP** (not HTTPS) — potential security concern.
- **Non-atomic CSV writes.** If the script crashes mid-write, the CSV may be corrupted.

### Flood & landslide data
- **NCHMF warnings are snapshots.** Each hourly fetch captures the current state. Missed fetches = lost data.
- **CentralVN.Landslide is scoped to Huế + Đà Nẵng only.** Expanding requires new commune boundary data.
- **No commune code migration handling.** If NCHMF updates codes after administrative mergers, mapping to `boundary.geojson` breaks.
- **Flood extent data (VegaCosmos) has no API.** Must be requested manually per event.

### Rainfall data
- **NASA POWER resolution is coarse** (0.5° ≈ 50 km). Good for regional overviews, not precise impact mapping.
- **Takes 5–10 minutes per run** due to ~300 sequential API calls.

---

## 10. A More Complete System

The tools above were built incrementally — one story at a time. They work, but each maintains its own data copy, there is no shared query interface, and station coverage is limited.

A unified backend has been built that addresses these gaps:

- **Single database** (PostgreSQL + PostGIS) — stores storm tracks, water levels, lake storage, landslide warnings, historical tracks, and rainfall anomalies in one schema
- **Full station network** — all available VNDMS stations, not just the curated 16
- **REST API** — query any data by location, time range, or storm ID with a single HTTP call
- **Automated crawlers** for all sources (JTWC, JMA, VNDMS, Thuy Loi, NCHMF, IBTrACS) on GitHub Actions cron
- **Alert mode** — auto-increases crawl frequency when a storm enters the Vietnam watch zone (95–120°E, 5–28°N)
- **No CSV growth problem** — proper time-series tables with indexing and data retention

The existing frontends can connect to this API with minimal changes — swap CSV reads for API calls.

If the team wants to explore this, contact **Tue (lqtue@gmail.com)** for API access. No setup or registration required — just a URL and a read-only key.

---

*Last updated: March 2026 — Spotlight/VnExpress Data Team*
