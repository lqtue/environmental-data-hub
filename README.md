# Spotlight Environmental Data Hub

Central index for all environmental and disaster data projects across the Spotlight team. Each project lives in its own repository — this hub links them together, documents how data flows between them, and provides shared technical guides.

---

## Projects

### Air Quality

| Repo | Description | Data source | Status |
|---|---|---|---|
| [spotlightvne/HanoiAQ](https://github.com/spotlightvne/HanoiAQ) | Ward-level PM2.5 map for Hanoi with cigarette-equivalent exposure | [GEOI](https://geoi.edu.vn/vi/) (VNU University of Engineering and Technology) | Active — data provided by GEOI |

### Typhoon Tracking

| Repo | Description | Data source | Status |
|---|---|---|---|
| [lqtue/environmental-data-hub](https://github.com/lqtue/environmental-data-hub) | Real-time typhoon dashboard + historical landfall analysis | JTWC, JMA, IBTrACS (NOAA), NASA POWER | Active |

**Scripts available:** `typhoon/` module contains all processing scripts.

**Colab (dành cho biên tập viên — không cần cài đặt):**

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/lqtue/environmental-data-hub/blob/main/notebooks/typhoon_analysis.ipynb)

### Crawlers (Unified)

| Repo | Description | Data source | Status |
|---|---|---|---|
| [lqtue/environmental-data-hub](https://github.com/lqtue/environmental-data-hub) | Consolidated Python crawlers for lake water, river levels, and landslide warnings | VNDMS, Thuy Loi Vietnam, NCHMF | Active |

**Scripts available:** `crawlers/` module contains `lake_water.py`, `river_water.py`, and `landslide.py`.

**Colab (dành cho biên tập viên — không cần cài đặt):**

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/lqtue/environmental-data-hub/blob/main/notebooks/crawlers.ipynb)

### Water Levels, Reservoirs & Flood/Landslide Warnings

| Repo | Description | Data source | Status |
|---|---|---|---|
| [vnexpress-spotlight/WaterDashboard](https://github.com/vnexpress-spotlight/WaterDashboard) | River water levels (16 stations) + lake storage (22 reservoirs) across Central Vietnam | VNDMS, Thuy Loi Vietnam | Active — GitHub Actions runs hourly, auto-creates PRs |
| [vnexpress-spotlight/CentralVN.Landslide](https://github.com/vnexpress-spotlight/CentralVN.Landslide) | Commune-level landslide + flash flood risk map (Huế & Đà Nẵng) | NCHMF | Active — hourly snapshots via WaterDashboard crawler |

**Basins covered:** Sê San · Hương–Bồ · Vu Gia–Thu Bồn · Trà Khúc · Kôn–Hà Thanh · Ba · Cái

### EV Transition

| Repo | Description | Data source | Status |
|---|---|---|---|
| [lqtue/environmental-data-hub](https://github.com/lqtue/environmental-data-hub) | Vietnam-specific lifecycle GHG comparison: BEV vs PHEV vs ICEV for cars and motorbikes | IEA LCA methodology, GREET, Vietnam grid data | In development |

**Methodology:** `docs/ev-lca-methodology-vietnam.md` — covers vehicle manufacturing, battery production, well-to-tank (Vietnam coal-heavy grid), and tank-to-wheel emissions for the Vietnamese market, including two-wheelers.

### Flood Mapping

| Repo | Description | Data source | Status |
|---|---|---|---|
| [spotlightvne/floodmap](https://github.com/spotlightvne/floodmap) | Flood extent visualization (Northern VN, deck.gl) | VegaCosmos satellite imagery, manual | Per-event |
| [vnexpress-spotlight/FloodViz](https://github.com/vnexpress-spotlight/FloodViz) | Flood data visualization (minimal) | — | Archive |
| [vnexpress-spotlight/FloodViz2](https://github.com/vnexpress-spotlight/FloodViz2) | Immersive flood storytelling dashboard with timeline | Rain/river/water data + narrative | Per-event |
| [vnexpress-spotlight/MuaMienTrung](https://github.com/vnexpress-spotlight/MuaMienTrung) | Central VN rainfall | — | Empty |

---

## How data flows between projects

```
                    ┌─────────────────────────────┐
                    │     External Data Sources    │
                    └──────────┬──────────────────┘
                               │
        ┌──────────┬───────────┼───────────┬──────────────┐
        ▼          ▼           ▼           ▼              ▼
    JTWC/JMA    VNDMS     Thuy Loi     NCHMF     GEOI / VegaCosmos
    (typhoon)   (rivers)  (lakes)   (warnings)   (AQ / flood extent)
        │          │           │           │              │
        ▼          └─────┬─────┴───────────┘              │
  environmental-data-hub │                                │
  typhoon/         crawlers/                              │
  notebooks/       notebooks/                             │
        │                │                                │
        │                │          ┌──────┘       ┌──────┘
        │                │          ▼              ▼
        │                │    CentralVN.      HanoiAQ
        │                │    Landslide       floodmap
        │                │          │
        ▼                ▼          ▼
  ┌──────────────────────────────────────┐
  │        Story / Article Layer         │
  │  FloodViz2, 2025typhon2, floodmap   │
  │  (story.json + narrative text)       │
  └──────────────────────────────────────┘
```

---

## Documentation

| Guide | What it covers |
|---|---|
| [docs/disaster-data-guide.md](docs/disaster-data-guide.md) | Full technical guide: all 7 data sources, API endpoints, processing scripts, typical workflows, known limitations |
| [docs/ev-lca-methodology-vietnam.md](docs/ev-lca-methodology-vietnam.md) | Vietnam-adapted lifecycle GHG methodology: vehicle manufacturing, battery production, grid emissions, fuel economy assumptions |

---

## Data sources reference

| Source | Website | Data type | Access | Used by |
|---|---|---|---|---|
| **JTWC** | metoc.navy.mil/jtwc | Real-time typhoon track + forecast | Public (RSS + text/KMZ) | environmental-data-hub |
| **JMA** | jma.go.jp | Typhoon position fallback | Public (JS endpoint, active season only) | environmental-data-hub |
| **IBTrACS** | ncei.noaa.gov | Historical storm tracks (1841–present) | Public download | environmental-data-hub |
| **NASA POWER** | power.larc.nasa.gov | Daily precipitation + 30-year climatology | Public API, no key needed | environmental-data-hub |
| **VNDMS** | vndms.dmptc.gov.vn | River water levels | Public (requires spoofed headers) | WaterDashboard |
| **Thuy Loi Vietnam** | e15.thuyloivietnam.vn | Lake/reservoir levels, storage, discharge | Public (HTTP only) | WaterDashboard |
| **NCHMF** | luquetsatlo.nchmf.gov.vn | Flash flood + landslide warnings | Public API | WaterDashboard, CentralVN.Landslide |
| **GEOI** | geoi.edu.vn | Modeled ward-level PM2.5 | By arrangement — data exchange | HanoiAQ |
| **VegaCosmos** | — | Satellite flood extent polygons | By request per event | floodmap |

---

## Known cross-cutting issues

- **Data is fragmented across repos.** Each project maintains its own crawlers, CSVs, and GeoJSON files. There is no shared query interface.
- **CSV storage grows unboundedly** in WaterDashboard and CentralVN.Landslide. Consider pruning at the start of each season.
- **Two GitHub accounts** (`vnexpress-spotlight` and `spotlightvne`) — historical split. Environmental projects exist on both.
- **No automated correlation** between typhoon position, water levels, and flood warnings — cross-referencing requires manual work.

---

## Potential upgrade: unified backend

The current setup is fragmented — each project has its own crawlers and CSV files. A unified backend could consolidate everything:

- Single PostGIS database for all data sources (storms, water levels, lakes, warnings, historical tracks, rainfall)
- Full station network — not just the selected 16 stations / 22 lakes
- Query by location, time range, or storm ID with one HTTP call
- GitHub Actions crawlers with alert mode (auto-increases frequency during active storms)
- No CSV growth — proper time-series storage with indexing

The existing frontends could connect to such an API with minimal changes.

---

*Maintained by Spotlight Data Team, VnExpress*
