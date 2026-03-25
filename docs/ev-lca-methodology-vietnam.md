# EV Life Cycle Assessment: Methodology for Vietnam

**Spotlight / VnExpress — Draft Methodology**

Adapted from the [IEA Global EV Data Explorer LCA Calculator Methodology](https://www.iea.org/data-and-statistics/data-tools/global-ev-data-explorer) for the Vietnamese market.

---

## 1. Overview

This methodology describes how to estimate the total lifecycle greenhouse gas (GHG) emissions of vehicles sold in Vietnam, comparing battery electric vehicles (BEV), hybrid electric vehicles (HEV), plug-in hybrid electric vehicles (PHEV), and internal combustion engine vehicles (ICEV). The goal is to produce a data-driven, Vietnam-specific comparison that readers can interact with — e.g. "Is an electric car actually greener in Vietnam, given how much coal we burn for electricity?"

The assessment covers emissions from **cradle to grave**:

```
┌─────────────────────────────────────────────────────────────┐
│                    Total Lifecycle Emissions                 │
│                                                             │
│  ┌──────────────────────┐   ┌────────────────────────────┐  │
│  │    Vehicle Cycle      │   │       Fuel Cycle            │  │
│  │                      │   │                            │  │
│  │  ● Vehicle body      │   │  ● Fuel production         │  │
│  │    manufacturing     │   │    (well-to-tank)          │  │
│  │                      │   │                            │  │
│  │  ● Battery           │   │  ● Fuel consumption        │  │
│  │    manufacturing     │   │    (tank-to-wheel)         │  │
│  └──────────────────────┘   └────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

### Why Vietnam is different

Vietnam's LCA result diverges significantly from Europe or the US because of three factors:

1. **Coal-heavy electricity grid** — 48% of power produced from coal (2024), with a grid emission factor estimated at **0.75–0.85 tCO₂e/MWh**. In Q1 2025 coal reached 56.5% due to dry season (low hydro). This means charging an EV in Vietnam produces far more upstream emissions than in France (nuclear) or Norway (hydro).

2. **Motorbike-dominant fleet** — 93.3% of registered vehicles are motorbikes. Vietnam is the **3rd largest electric motorcycle market globally**. Any meaningful LCA must include two-wheelers (electric scooters vs. petrol motorbikes), not just cars.

3. **VinFast as dominant domestic EV manufacturer** — VinFast sold 87,000 electric cars domestically in 2024 (+150% YoY), capturing 17.6% of the overall automobile market. VinFast also sold 400,000+ electric motorbikes in 2025 (~5× YoY growth). Battery chemistry uses both LFP (Gotion High-Tech partnership) and NMC (CATL partnership), with the VinES battery manufacturing facility ($173.7M investment) in Vung Ang producing 100,000 packs/year.

### Vietnam EV market snapshot (2024–2025)

| Metric | Value | Source |
|---|---|---|
| EV car sales, H1 2024 | ~17,500 units (exceeded all of 2023) | VAMA |
| VinFast domestic sales, 2024 | 87,000 units (+150% YoY) | VinFast |
| VinFast market share (all cars) | 17.6% (2024) | VinFast |
| VinFast e-motorbike sales, 2025 | 400,000+ units (+532% YoY) | Kirin Capital |
| E-motorbike market share | VinFast 32%, Pega 15–16%, Yadea 12–13% | Kirin Capital |
| Total market size | $3.02B (2024), projected $12.23B by 2033 | IMARC |
| Government target | 50% EV penetration in urban areas by 2030 | MOIT |
| Hanoi ICE motorbike ban | Announced from mid-2026 | Hanoi People's Committee |

### Key government incentives (current as of 2025)

| Incentive | Detail | Period |
|---|---|---|
| Registration fee exemption | 100% exemption for BEV | Through Feb 2027 (Decree 51/2025) |
| Special consumption tax (SCT) | 1–3% for BEV (vs. 35–150% for ICEV by engine size) | Through Feb 2027 |
| SCT post-incentive | 4–11% for BEV | From Mar 2027 |
| HEV excise tax | 70% of equivalent ICEV rate | From 2026 |
| Import duty | 0% for BEV (vs. 70% for CBU ICEV) | Ongoing |
| Road use fee | BEV exempt | Ongoing |

---

## 2. System Boundaries

### Vehicle types covered

Unlike the IEA tool (which covers only passenger cars), this Vietnam adaptation includes **both four-wheelers and two-wheelers**:

| Segment | Examples | Powertrains |
|---|---|---|
| **Motorbike / Scooter** | Honda Wave, VinFast Klara, Yadea | ICEV, BEV |
| **Small car** (A/B segment) | VinFast VF 5, Hyundai i10 | BEV, HEV, ICEV |
| **Medium car** (C/D segment) | VinFast VF e34, Toyota Vios, Honda City e:HEV, Toyota Camry Hybrid | BEV, HEV, PHEV, ICEV |
| **Large car / SUV** | VinFast VF 8/9, Toyota Fortuner, Toyota Corolla Cross HEV | BEV, HEV, PHEV, ICEV |

### Emissions categories

| Category | Subcategory | What it covers |
|---|---|---|
| **Vehicle cycle** | Vehicle manufacturing | Steel, aluminium, plastic, rubber, glass, copper — extraction, processing, assembly |
| | Battery manufacturing | Cathode/anode materials, cell production, pack assembly |
| **Fuel cycle** | Well-to-tank (WTT) | Extraction/refining of gasoline/diesel; or electricity generation + grid losses for BEV |
| | Tank-to-wheel (TTW) | Tailpipe CO₂ from combustion (zero for BEV) |

### What is excluded

- Vehicle end-of-life and recycling (insufficient data for Vietnam)
- Battery second-life applications
- Indirect land use change (ILUC) from biofuels
- Non-CO₂ pollutants (PM2.5, NOx) — though these are covered separately by the HanoiAQ project
- Infrastructure (road construction, charging station manufacturing)

---

## 3. Vehicle Manufacturing Emissions

### Vehicle mass

Vehicle mass (excluding battery) determines manufacturing emissions. Values are adapted from GREET (2022) and IEA, with adjustments for the Vietnam market where Vietnamese-manufactured vehicles differ.

**Four-wheelers (kg, excluding EV battery):**

| Size | BEV | HEV | PHEV | ICEV |
|---|---|---|---|---|
| Small | 840 | — | — | 1,030 |
| Medium | 1,250 | 1,480 | 1,600 | 1,420 |
| Large / SUV | 1,530 | 1,810 | 2,010 | 1,740 |

*Note: HEV is heavier than ICEV due to electric motor + battery + power electronics, but lighter than PHEV (smaller battery, no plug-in charging system).*

**Two-wheelers (kg, excluding EV battery):**

| Type | BEV | ICEV |
|---|---|---|
| Scooter / underbone | 75–90 | 95–110 |
| Motorbike (>125cc equivalent) | 100–130 | 120–150 |

### Material composition

Material shares by powertrain (from GREET 2022), used to compute manufacturing emissions per material:

| Material | BEV | HEV | PHEV | ICEV |
|---|---|---|---|---|
| Steel | 66% | 62% | 61% | 63% |
| Aluminium | 13% | 13% | 14% | 13% |
| Copper | 4% | 3% | 6% | 2% |
| Glass | 2% | 2% | 2% | 2% |
| Plastic | 12% | 16% | 13% | 16% |
| Rubber | 3% | 4% | 3% | 4% |

*Note: HEV material composition is closer to ICEV than to PHEV/BEV, as it retains a full ICE drivetrain with a smaller electric assist system.*

Manufacturing emission intensities use GREET defaults adjusted to global weighted averages (not US-specific), following IEA's approach.

### Formula

```
Vehicle_mfg_emissions (tCO₂e) = Σ (material_share × vehicle_mass × emission_intensity_per_kg)
```

For two-wheelers, the same material-share approach applies but with lower total mass and a simplified material mix (more steel/plastic, less aluminium).

---

## 4. Battery Manufacturing Emissions

### Battery chemistry

The dominant EV battery chemistries in the Vietnam market:

| Chemistry | Used by | Share of emissions from production |
|---|---|---|
| **LFP** (Lithium Iron Phosphate) | VinFast (most models), Gotion High-Tech partnership, most Chinese-import EVs | ~40% of total battery emissions |
| **NMC** (Nickel Manganese Cobalt) | VinFast VF 8 (87.7 kWh CATL NMC pack), some imported EVs (Hyundai, BMW) | ~15% of total battery emissions |
| **NiMH** (Nickel Metal Hydride) | Toyota HEV models (Camry Hybrid, Corolla Cross HEV, Yaris Cross) | Lower than Li-ion per kWh but small capacity |
| **Lead-acid / small lithium** | Electric scooters (Klara, Yadea, Pega) | Varies widely |

**VinFast battery supply chain:** VinFast partners with Gotion High-Tech (LFP R&D), CATL (NMC cells + skateboard chassis), ProLogium (solid-state R&D), and StoreDot (extreme fast charging). The VinES Battery Manufacturing Facility in Vung Ang Economic Zone ($173.7M, 8 hectares) produces 100,000 battery packs/year. Over 98% of global LFP cathode material and cells are currently produced in China.

**Key parameters (from IEA/GREET):**

| Parameter | Value |
|---|---|
| Battery pack carbon intensity | ~90 kg CO₂e per kWh (sales-weighted global mix) |
| Battery pack energy density | 150 Wh/kg |
| LFP vs NMC ratio | LFP produces roughly two-thirds of the emissions of high-nickel NMC |

### Battery size by vehicle type (Vietnam market)

| Vehicle | Typical battery (kWh) | Source |
|---|---|---|
| Electric scooter | 1.2–3.5 | VinFast Klara S: 1.38 kWh; Yadea: 2.2 kWh |
| HEV (medium car) | 0.9–1.6 | Toyota Camry Hybrid: 1.6 kWh NiMH; Honda City e:HEV: 0.86 kWh Li-ion |
| HEV (SUV/crossover) | 1.0–1.8 | Toyota Corolla Cross HEV: 1.3 kWh NiMH; Toyota Yaris Cross: 1.0 kWh |
| VinFast VF 5 | 37.2 | VinFast specs |
| VinFast VF e34 | 42 | VinFast specs |
| VinFast VF 8 | 82 (Eco) / 87.7 (Plus) | VinFast specs |
| VinFast VF 9 | 92 (Eco) / 123 (Plus) | VinFast specs |

### Formula

```
Battery_mfg_emissions (tCO₂e) = battery_capacity_kWh × carbon_intensity_per_kWh
```

For LFP batteries, use ~60 kg CO₂e/kWh; for NMC, use ~90 kg CO₂e/kWh.

### Battery replacement

Per IEA methodology: if the vehicle owner replaces the battery (assumed after 10 years or 160,000 km), the replacement battery benefits from:
- 30% higher energy density (technology improvement)
- 20% recycled cathode material
- Lower grid carbon intensity at time of replacement

This adds a second battery manufacturing emission event, reduced by roughly 20–30% compared to the original.

---

## 5. Fuel Production Emissions (Well-to-Tank)

### 5.1 Gasoline and Diesel

Well-to-tank emissions cover extraction, refining, and transport of fossil fuels. Vietnam-specific factors:

- Vietnam is a **net energy importer** — crude oil is imported (Dung Quất and Nghi Sơn refineries process ~60% of domestic demand; the rest is imported as refined product)
- Domestic refining uses a mix of Vietnamese crude and imported crude (Middle East, Russia)
- Vietnam mandates **E5 gasoline** (5% ethanol blend) nationwide since 2018

| Fuel | WTT emission factor | Notes |
|---|---|---|
| Gasoline (RON 95-III, E5) | ~0.5–0.7 kg CO₂e/litre | Includes refining + ethanol production |
| Diesel (DO 0.05S) | ~0.5–0.6 kg CO₂e/litre | Domestic + imported |

**Biofuel component:**
- Vietnam's E5 uses ethanol primarily from **cassava and sugarcane molasses** (Asia and Pacific feedstock mix per IEA)
- The biofuel share is small (5% by volume) so its impact on total WTT emissions is modest
- ILUC (indirect land use change) is not included, consistent with IEA methodology

### 5.2 Electricity (for BEV charging)

This is the **critical factor** for Vietnam's LCA. The well-to-tank emissions for a BEV are entirely determined by the carbon intensity of the electricity grid.

**Vietnam grid emission factor (tCO₂e/MWh):**

| Year | Emission factor | Source | Grid mix highlights |
|---|---|---|---|
| 2020 | 0.90 | World Bank CCDR (2022) | Coal 59%, hydro 25%, gas 13% |
| 2024 | 0.75–0.85 | Estimated from generation mix | Coal 48%, hydro 31%, solar 8%, wind 4% |
| Q1 2025 | 0.80–0.90 | EVN Q1 report | Coal 56.5% (dry season), hydro 19.1%, RE 16% |
| 2030 (Revised PDP8) | 0.55–0.65 | Decision 768/2025 | Emissions capped at 197–199 MtCO₂ |
| 2030 (ADS) | 0.35–0.40 | World Bank modeling | Coal ~20%, renewables ~55% |
| 2040 (NZP) | 0.15–0.25 | Net-zero pathway | Coal <10%, renewables 70%+ |
| 2050 (net-zero) | ~0.05 | Vietnam COP26 commitment | Target: 27 MtCO₂ from power sector |

**Note:** The Revised PDP8 (Decision 768/QD-TTg, April 2025) supersedes the original PDP8 (Decision 500/2023) with more aggressive renewables targets and stricter emissions caps.

**Electricity generation mix (2024):**
```
Coal:   48%  ████████████████████████
Hydro:  31%  ████████████████
Solar:   8%  ████
Wind:    4%  ██
Gas:     7%  ████
Other:   2%  █
```

**Why the grid factor matters so much:**
With a grid EF of 0.90, a BEV consuming 15 kWh/100 km produces **135 g CO₂e/km** from electricity alone — comparable to a fuel-efficient ICEV. As Vietnam decarbonizes its grid (PDP8 targets), this number drops dramatically, making the EV advantage grow over time.

### Charging losses

Per IEA methodology, a **2% additional energy consumption** is applied to BEV fuel economy to account for grid-to-charger losses. Vietnam's grid operates at 220V/50Hz; home charging (Level 1/2) dominates.

---

## 6. Fuel Consumption Emissions (Tank-to-Wheel)

### Tailpipe emissions

| Fuel | CO₂ per litre |
|---|---|
| Gasoline (E5) | ~2.2 kg CO₂/litre (reduced from 2.3 due to 5% ethanol) |
| Diesel | 2.7 kg CO₂/litre |
| Electricity | 0 (tailpipe — upstream counted in WTT) |

Biofuel combustion is treated as carbon-neutral (biogenic carbon), consistent with IEA methodology.

### Fuel economy assumptions for Vietnam

Fuel economy varies significantly with driving conditions. Vietnam's urban-dominant driving pattern (especially in Hanoi and HCMC) affects both ICEV and BEV efficiency differently:

- **ICEV**: Urban stop-and-go driving **worsens** fuel economy (more idling, braking waste)
- **HEV**: Urban stop-and-go driving **benefits** HEVs the most — regenerative braking recaptures energy, and the electric motor handles low-speed driving where ICE is least efficient. This makes HEVs particularly well-suited to Vietnamese urban traffic.
- **BEV**: Urban driving can **improve** efficiency (regenerative braking), but high AC usage in tropical heat **reduces** range

**Four-wheelers (per 100 km):**

| Size | BEV (kWh) | HEV gasoline (litres) | ICEV gasoline (litres) | ICEV diesel (litres) |
|---|---|---|---|---|
| Small | 13–16 | 4.0–5.5 | 6.0–7.5 | — |
| Medium | 16–20 | 4.5–6.0 | 7.0–9.0 | 5.5–7.0 |
| Large / SUV | 20–26 | 5.5–7.5 | 9.0–12.0 | 7.0–9.5 |

*Note: HEV fuel economy is typically 25–40% better than equivalent ICEV, with the improvement most pronounced in urban driving conditions like those in Hanoi and HCMC. Toyota claims 4.3 L/100km for the Camry Hybrid and 4.5 L/100km for the Corolla Cross HEV (WLTC combined).*

**Two-wheelers (per 100 km):**

| Type | BEV (kWh) | ICEV (litres) |
|---|---|---|
| Scooter / underbone | 1.5–2.5 | 1.8–2.5 |
| Motorbike (>125cc equiv.) | 3.0–5.0 | 2.5–3.5 |

**Climate correction:**
A **1.1× correction factor** is applied to WLTC-based fuel economy values (per IEA), plus an additional factor for tropical AC load:
- BEV in Vietnam: +10–15% energy consumption vs. WLTC due to continuous AC
- ICEV in Vietnam: +5–10% due to AC compressor load

### Vietnam-specific driving assumptions

| Parameter | Value | Rationale |
|---|---|---|
| Average annual distance (car) | 15,000–20,000 km | Vietnamese market estimate |
| Average annual distance (motorbike) | 8,000–12,000 km | Urban commuter pattern |
| Vehicle lifetime | 15 years (car), 10 years (motorbike) | Vietnamese registration data |
| Lifetime distance (car) | 200,000 km | Conservative; no inspection regime before 2024 |
| Lifetime distance (motorbike) | 100,000 km | High turnover rate |
| PHEV utility factor | 30–40% | Lower than global average (40%) due to limited charging infrastructure |

---

## 7. Putting It Together: Total Lifecycle Calculation

### Formula

```
Total_lifecycle_emissions (tCO₂e) =
    Vehicle_manufacturing
  + Battery_manufacturing (BEV/HEV/PHEV only)
  + (WTT_per_km × lifetime_km)
  + (TTW_per_km × lifetime_km)
  + Battery_replacement (optional, after 10 years; not applicable for HEV)
```

*Note: HEV battery manufacturing emissions are included but are minimal (~0.1 t) due to the very small battery size (0.9–1.8 kWh). HEV batteries typically last the lifetime of the vehicle and do not require replacement.*

### Example: Medium car, 200,000 km lifetime, Vietnam 2025 grid

| Component | BEV (VF e34-class) | HEV (Camry Hybrid-class) | ICEV (Vios-class) |
|---|---|---|---|
| Vehicle manufacturing | 6.5 t | 7.8 t | 7.5 t |
| Battery manufacturing | 2.5 t (42 kWh LFP) | 0.1 t (1.6 kWh NiMH) | — |
| WTT (fuel production) | 24.0 t ¹ | 5.2 t ³ | 8.0 t |
| TTW (tailpipe) | 0 t | 17.2 t ⁴ | 26.6 t ² |
| **Total** | **33.0 t** | **30.3 t** | **42.1 t** |
| **Per km** | **165 g/km** | **152 g/km** | **211 g/km** |

¹ 42 kWh battery, 18 kWh/100km × 1.02 loss × 200,000 km × 0.78 tCO₂e/MWh grid EF (2025 est.)
² 8 L/100km × 200,000 km × 2.2 kg CO₂/L × (1 + 0.3 WTT ratio)
³ 5.2 L/100km × 200,000 km × 0.6 kg CO₂e/L WTT factor (gasoline only, no grid dependency)
⁴ 5.2 L/100km × 200,000 km × 2.2 kg CO₂/L × (1 − 0.05 biofuel credit) × correction

**Key insight:** On Vietnam's coal-heavy grid (2025), the HEV actually edges out the BEV in lifecycle emissions (152 vs. 165 g/km) because HEVs achieve dramatic fuel savings without any grid electricity dependency. As Vietnam decarbonizes its grid, the BEV advantage grows — by 2030, BEV drops to ~120 g/km while HEV remains at ~152 g/km. By 2050, the BEV reaches ~60 g/km. The HEV's advantage is that it delivers immediate, grid-independent emission reductions with no charging infrastructure required — a significant practical advantage in Vietnam where public charging remains limited outside major cities.

### Two-wheeler comparison

| Component | BEV scooter | Petrol scooter |
|---|---|---|
| Vehicle manufacturing | 0.4 t | 0.5 t |
| Battery manufacturing (2 kWh) | 0.12 t | — |
| WTT | 1.4 t | 0.7 t |
| TTW | 0 t | 4.0 t |
| **Total (100,000 km)** | **1.9 t** | **5.2 t** |
| **Per km** | **19 g/km** | **52 g/km** |

**The two-wheeler case is decisive:** Even on Vietnam's dirty grid, an electric scooter produces **63% less lifecycle CO₂** than a petrol scooter. This is because petrol scooter engines are extremely inefficient (small displacement, no catalytic converter on most Vietnamese bikes).

---

## 8. Electricity Pricing & Total Cost of Ownership

Beyond lifecycle emissions, the **cost comparison** between BEV and ICEV is critical for Vietnamese consumers. Vietnam's unique electricity pricing structure fundamentally shapes the economics of EV ownership.

### 8.1 Vietnam's electricity tariff structure

Vietnam uses an **increasing block rate (IBR)** — the more you consume, the higher the marginal price. This directly affects EV charging costs at home.

**Residential electricity tariff (6 tiers, as of 2024):**

| Tier | Consumption block | Price (VND/kWh) | ~USD cents/kWh |
|---|---|---|---|
| Tier 1 | ≤ 50 kWh | 1,893 | 7.6 |
| Tier 2 | 51–100 kWh | 1,956 | 7.8 |
| Tier 3 | 101–200 kWh | 2,271 | 9.1 |
| Tier 4 | 201–300 kWh | 2,860 | 11.4 |
| Tier 5 | 301–400 kWh | 3,197 | 12.8 |
| Tier 6 | > 400 kWh | 3,302 | 13.2 |

*Prices subject to 10% VAT. Source: EVN, updated periodically by MOIT.*

**Key insight from Le Viet Phu (2020):** Vietnam's average retail electricity price (~8.1 US cents/kWh as of 2019) is among the **lowest in the world** — far below the long-run marginal cost of production (9.37 cents/kWh per ADB estimate). This implicit subsidy makes home EV charging very cheap, but it also means:

- EVN operates at a loss on residential electricity, which is **not sustainable** as EV adoption grows
- Future tariff reforms will likely raise electricity prices, narrowing the cost advantage
- The IBR structure means that EV charging pushes households into **higher tiers** — a household already consuming 200 kWh/month that adds 150 kWh for EV charging will pay Tier 4–5 rates for the marginal kWh

### 8.2 Electricity demand elasticity (Le Viet Phu, 2020)

A 2020 study by Le Viet Phu (Fulbright University Vietnam), published in *Environmental Economics and Policy Studies*, provides the first household-level estimate of electricity demand in Vietnam using World Bank VHRS microdata (5,000 households across Hanoi, HCMC, Da Nang, Binh Duong, and Dak Nong).

**Key econometric findings:**

| Parameter | Estimate | Interpretation |
|---|---|---|
| Own-price elasticity (average price) | −0.89 to −1.10 | Nearly unitary — demand responds proportionally to price |
| Own-price elasticity (marginal price) | −1.06 to −2.08 | More elastic to marginal price than average price |
| Income elasticity | 0.05–0.08 | Low — electricity is a **necessity**, not a luxury |
| Cross-price elasticity (substitutes: LPG, wood, coal) | 0.04–0.06 | Low — limited substitutability |

**Implications for EV economics:**
1. **Price sensitivity is real.** Unlike common assumptions, Vietnamese households *do* respond to electricity price signals. A tariff increase will moderate demand and affect EV charging behaviour.
2. **Electricity is a necessity** (low income elasticity), meaning higher-income households with EVs will absorb price increases rather than stop charging.
3. **IBR structure creates a progressive cost burden** — EV-owning households (typically higher-income) will pay Tier 5–6 rates for marginal charging kWh, partially self-targeting the subsidy.

### 8.3 Cost of charging vs. fueling

**Home charging cost (car, per 100 km):**

| Scenario | BEV consumption | Effective rate | Cost per 100 km |
|---|---|---|---|
| Household at Tier 3 baseline (+EV at Tier 4) | 18 kWh | 2,860 VND/kWh | 51,480 VND (~$2.06) |
| Household at Tier 4 baseline (+EV at Tier 5–6) | 18 kWh | 3,200 VND/kWh | 57,600 VND (~$2.30) |
| VinFast public fast charging | 18 kWh | ~3,500–4,500 VND/kWh | 63,000–81,000 VND (~$2.52–$3.24) |

**Petrol cost (car, per 100 km):**

RON95-III has fluctuated between 19,006 and 30,690 VND/L in 2025–2026. Using mid-range estimate of ~25,000 VND/L:

| Vehicle | Consumption | Fuel price (RON 95-III) | Cost per 100 km |
|---|---|---|---|
| HEV sedan (Camry Hybrid) | 4.5–5.5 L | ~25,000 VND/L | 112,500–137,500 VND (~$4.50–$5.50) |
| Fuel-efficient ICEV (Vios) | 7 L | ~25,000 VND/L | 175,000 VND (~$7.00) |
| Average ICEV sedan | 8.5 L | ~25,000 VND/L | 212,500 VND (~$8.50) |
| ICEV SUV | 11 L | ~25,000 VND/L | 275,000 VND (~$11.00) |

**Running cost ranking:** BEV home charging (51k–58k VND/100km) is cheapest, followed by HEV (113k–138k VND/100km) at roughly **half the cost of an equivalent ICEV**. The HEV advantage over ICEV requires no infrastructure change — just fuelling at the same petrol station with fewer visits.

**Two-wheeler running cost:**

| Type | Consumption | Cost per 100 km |
|---|---|---|
| Electric scooter (home charge, Tier 3) | 2 kWh | 4,540 VND (~$0.18) |
| Petrol scooter (Honda Wave) | 2 L | 50,000 VND (~$2.00) |

The electric scooter is **~10× cheaper to fuel** than a petrol scooter — the most compelling consumer argument in a price-sensitive market.

### 8.4 Total Cost of Ownership (TCO) framework

A complete TCO comparison should include:

```
TCO = Purchase_price
    + Registration_tax_and_fees
    + Fuel/charging_costs (lifetime)
    + Maintenance_costs (lifetime)
    + Insurance (lifetime)
    − Residual_value
    − Government_incentives
```

**Vietnam-specific TCO factors:**

| Factor | BEV | HEV | ICEV | Notes |
|---|---|---|---|---|
| Registration tax | Exempt 2022–2027 | Standard rate | Standard rate | BEV saves 10–15% of vehicle price |
| Special consumption tax | 1–3% (through 2027) | 70% of ICEV rate | 35–150% by engine size | HEV gets partial tax benefit from 2026 |
| Import duty | 0% | 70% (CBU) | 70% (CBU) | Applies to imports only |
| Road use fee | Exempt | Standard | Standard | BEV saves 1.5–3.6M VND/year |
| Maintenance | ~40% lower | ~15% lower | Baseline | HEV has regenerative braking (less brake wear) but still has ICE maintenance |
| Fuel cost | 65–75% lower | 25–40% lower | Baseline | HEV saves via better fuel economy, no electricity cost |
| Battery replacement | Risk (after 10yr) | Negligible | N/A | HEV battery is small, lasts vehicle lifetime; BEV: VinFast offers subscription |
| Residual value | Uncertain | Strong | Established | Toyota HEVs hold value well globally; BEV secondary market still forming |
| Purchase price | Premium | Moderate premium | Baseline | HEV typically 15–25% over ICEV; BEV 30–60% over ICEV (before incentives) |

### 8.5 Future electricity price trajectory

The current low electricity price is unlikely to persist. Per the World Bank CCDR (2022):

- Under the Accelerated Decarbonization Scenario (ADS), the levelized cost of electricity could be **26% higher by 2040** and **16% higher on average** between 2020–2040
- Tariff reform is needed to make EVN financially viable and to fund the energy transition
- Carbon pricing ($12–$120/tCO₂e range modeled) would further increase electricity costs

However, even with a 30% increase in electricity prices, BEV running costs would still be **2–3× cheaper** than petrol at current fuel prices.

---

## 9. Sensitivity Analysis: Key Variables

The calculator should allow users to adjust these parameters:

| Parameter | Default (Vietnam 2025) | Range | Impact |
|---|---|---|---|
| Grid emission factor | 0.78 tCO₂e/MWh | 0.05–0.95 | **Highest impact** — determines whether BEV wins |
| Annual driving distance | 15,000 km (car) | 5,000–30,000 | More driving favours BEV |
| Vehicle lifetime | 15 years | 8–20 years | Longer life favours BEV |
| Battery size | Model-specific | ±30% | Larger battery = more mfg emissions |
| Battery chemistry | LFP | LFP / NMC | NMC ~50% higher mfg emissions |
| Fuel economy (ICEV) | 8 L/100km | 5–15 L/100km | Worse ICEV economy favours BEV |
| BEV efficiency | 18 kWh/100km | 12–30 kWh/100km | Worse BEV efficiency narrows gap |
| HEV fuel economy | 5.2 L/100km | 4.0–7.0 L/100km | Better HEV economy narrows gap vs. BEV |
| PHEV utility factor | 35% | 0–70% | More electric driving favours PHEV |
| AC climate penalty | +12% (BEV), +7% (ICEV/HEV) | 0–20% | Tropical climate correction |

### Break-even grid emission factor

The grid EF at which a BEV and ICEV have equal lifecycle emissions (for a medium car, 200,000 km):

- **NMC battery**: break-even at ~1.05 tCO₂e/MWh
- **LFP battery**: break-even at ~1.15 tCO₂e/MWh

Vietnam's current grid (0.78–0.90) is **well below the break-even point**, meaning BEVs are already cleaner even on today's grid.

### BEV vs. HEV crossover point

The grid EF at which a BEV becomes cleaner than an HEV (medium car, 200,000 km, LFP battery):

- **Crossover at ~0.65 tCO₂e/MWh** — below this, BEV is cleaner than HEV
- Vietnam's current grid (0.78–0.90) is **above** this crossover, meaning HEV currently has a slight lifecycle advantage
- Under PDP8 2030 projections (0.55–0.65), BEV and HEV reach approximate parity
- By 2040+, BEV decisively outperforms HEV

This makes HEV a compelling "bridge technology" for Vietnam — delivering immediate emissions reductions while the grid decarbonizes, after which BEV takes the lead.

---

## 9. Data Sources

### Vietnam-specific

| Data | Source | Access |
|---|---|---|
| Grid emission factor | World Bank Vietnam CCDR (2022); EVN annual reports | Public |
| Vehicle registration stats | Vietnam Register; GSO | Public |
| HCMC vehicle fleet | UBND HCMC Report No. 75/BC-UBND (2024) | Public |
| Fuel prices | Petrolimex; MOIT announcements | Public |
| Electricity prices & demand elasticity | EVN tiered tariff; Le Viet Phu (2020) | Public / Academic |
| EV specifications | VinFast product pages; manufacturer specs | Public |
| PDP8 grid projections | Revised PDP8 (Decision 768/QD-TTg, April 2025) | Public |
| EV market data | VAMA; VinFast investor reports; IMARC; Kirin Capital | Mixed |
| Gasoline prices | Petrolimex; MOIT biweekly adjustment announcements | Public |
| Generation mix (2024) | EVN; Low Carbon Power; Ember | Public |
| EV policy / incentives | Decree 51/2025; Tilleke & Gibbins legal analysis | Public |

### International (methodology)

| Data | Source |
|---|---|
| Vehicle manufacturing emissions | GREET model (Argonne National Laboratory, 2022) |
| Battery carbon intensity | IEA GEVO LCA Calculator; Dai et al.; Degen et al. |
| Battery energy density | EV Volumes (2022 sales-weighted average) |
| Fuel economy baselines | IEA Global Fuel Economy Initiative (2021) |
| Biofuel emission intensities | IEA Renewables 2023; GREET |
| Upstream fuel emissions | IEA Life Cycle Upstream Emission Factors database |

---

## 10. Implementation Notes

### For the interactive calculator

The simplest implementation is a single-page web app where the user:
1. Selects **vehicle type** (scooter / small car / medium car / SUV)
2. Selects **powertrain** (BEV / HEV / PHEV / ICEV)
3. Sees a default Vietnam-specific result with a breakdown bar chart
4. Can toggle **grid scenario** (current / 2030 CPS / 2030 ADS / 2050 NZP)
5. Can adjust sliders for driving distance, lifetime, fuel economy

**Key editorial outputs:**
- "Mỗi km đi xe điện thải ra bao nhiêu CO₂?" (How much CO₂ per km for an EV?)
- Side-by-side lifecycle comparison: VinFast VF 5 vs. Hyundai i10
- HEV vs. BEV vs. ICEV: Toyota Camry Hybrid vs. VinFast VF e34 vs. Toyota Vios — which wins in Vietnam today?
- Electric scooter vs. Honda Wave — the decisive case
- Future projection: how the answer changes as Vietnam's grid gets cleaner (and when BEV overtakes HEV)

### Working prototype

A sample interactive calculator is available at [`interactive/ev-lca-calculator.html`](../interactive/ev-lca-calculator.html) ([live demo](https://lqtue.github.io/environmental-data-hub/interactive/ev-lca-calculator.html)). It implements the core methodology above as a single self-contained HTML page (vanilla JS, no dependencies). Features:

- Vehicle type selector: xe máy / xe nhỏ / xe trung / SUV with real Vietnam market examples
- Four-way powertrain comparison: BEV / HEV / PHEV / ICEV
- Grid scenario toggle (2025 → 2030 → 2040 → 2050) — demonstrates the BEV vs HEV crossover as grid decarbonizes
- Adjustable sliders: lifetime km, battery size, ICEV and BEV fuel economy
- Stacked bar chart with manufacturing / battery / WTT / TTW breakdown
- Running cost table (VND/100km) with savings vs ICEV
- Dynamic insight text explaining which powertrain wins and why

This prototype can be embedded directly in a VnExpress article via iframe or adapted into a more polished D3/Plotly version for production.

### Data pipeline

```
Static parameters          → JSON config (vehicle specs, emission factors)
Grid emission projections  → CSV/JSON (year × scenario × EF)
User inputs                → JavaScript sliders
Calculation                → Client-side (no backend needed)
Output                     → Stacked bar chart (Plotly / D3 / simple SVG)
```

### What still needs to be collected

| Data gap | How to fill | Priority |
|---|---|---|
| Vietnam-specific vehicle manufacturing EF | Use GREET defaults (acceptable approximation) | Low |
| Actual VinFast battery chemistry & sourcing | VinFast press releases / CATL partnership announcements | Medium |
| Real-world fuel economy in Vietnamese conditions | VinFast community forums; Ministry of Transport test data | High |
| Real-world HEV fuel economy in Vietnam | Toyota Vietnam; owner forums; MOIT test data | High |
| HEV sales data in Vietnam | VAMA; Toyota Vietnam; Honda Vietnam | Medium |
| Updated grid EF (post-PDP8 approval) | EVN annual report or MOIT statistics | High |
| E-scooter battery lifecycle data | Manufacturer warranty terms; field surveys | Medium |

---

## 11. Key Findings (Preview)

Based on this methodology, the headline findings for a Vietnam audience are:

1. **All electrified powertrains are cleaner than ICEV in Vietnam** — BEV (~22% less), HEV (~28% less), even with the coal-heavy grid. The story is not just about full electric.

2. **HEV is currently the lifecycle champion for cars** — on Vietnam's 2025 grid (0.78–0.90 tCO₂e/MWh), an HEV like the Camry Hybrid produces ~152 g/km vs. BEV at ~165 g/km, because HEVs achieve major fuel savings without any grid electricity dependency. This finding is counterintuitive and editorially powerful.

3. **But BEV will overtake HEV as the grid cleans up** — the crossover happens around 0.65 tCO₂e/MWh, expected by 2030 under PDP8. By 2040–2050, BEV is decisively cleaner. HEV is a bridge technology; BEV is the destination.

4. **Electric scooters are a clear win** — 60%+ reduction vs. petrol scooters regardless of grid mix. This is the most impactful story for Vietnamese readers because motorbikes are the dominant transport mode.

5. **The gap will widen dramatically** — under PDP8 scenarios, the BEV advantage over ICEV grows to 35–50% by 2030 and 70%+ by 2040 as coal exits the grid.

6. **Battery size matters** — a VF 9 (123 kWh battery) has significantly higher manufacturing emissions than a VF 5 (37 kWh). Right-sizing the vehicle is important.

7. **Vietnam's tropical climate is a double-edged sword** — continuous AC use increases BEV energy consumption by ~10–15%, partially offsetting the efficiency advantage. But it also increases ICEV and HEV fuel consumption, so the relative comparison is less affected than the absolute numbers.

8. **HEV requires zero infrastructure change** — unlike BEV which needs charging infrastructure (still limited outside Hanoi/HCMC), HEV uses existing petrol stations. For provincial Vietnam, this practical advantage is significant.

---

## References

- IEA (2024). *Global EV Data Explorer — LCA Calculator Methodology*
- World Bank (2022). *Vietnam Country Climate and Development Report*
- GREET Model, Argonne National Laboratory (2022)
- UBND TP.HCM (2024). *Báo cáo số 75/BC-UBND — Xe cá nhân 2009–2023*
- Dai, Q., et al. (2019). "Life Cycle Analysis of Lithium-Ion Batteries for Automotive Applications." *Batteries*, 5(2), 48.
- Degen, F., et al. (2023). "Energy consumption of current and future production of lithium-ion and post lithium-ion battery cells." *Nature Energy*.
- Frith, J.T., et al. (2023). "A non-academic perspective on the future of lithium-based batteries." *Nature Communications*.
- Le Viet Phu (2020). "Electricity price and residential electricity demand in Vietnam." *Environmental Economics and Policy Studies*, 22, 395–425. doi:10.1007/s10018-020-00267-6.
- Oh, J.E., et al. (2019). "Addressing Climate Change in Transport." *Vietnam Transport Knowledge Series*, World Bank.
- MOIT (2023). *Quy hoạch phát triển điện lực quốc gia thời kỳ 2021–2030 (PDP8)*

### Online sources (accessed March 2026)

- [Vietnam Electricity Generation Mix 2024](https://lowcarbonpower.org/region/Vietnam) — Low Carbon Power
- [Viet Nam energy data](https://ember-energy.org/countries-and-regions/viet-nam/) — Ember
- [Vietnam EV market statistics](https://www.statista.com/topics/10557/electric-vehicle-market-in-vietnam/) — Statista
- [Vietnam extends EV registration fee exemption until 2027](https://www.vietnam-briefing.com/news/vietnam-extends-ev-registration-fee-exemption-until-2027.html/) — Vietnam Briefing
- [Vietnam's legal framework on electric vehicles](https://www.tilleke.com/insights/vietnams-legal-framework-on-electric-vehicles-offers-new-opportunities-for-investors/) — Tilleke & Gibbins
- [VinFast leads way in EV battery optimisation](https://cleantechnica.com/2024/10/11/vinfast-leads-way-in-ev-battery-optimisation/) — CleanTechnica
- [VinFast partners with Gotion High-Tech in LFP battery cell R&D](https://vinfastauto.us/newsroom/press-release/vinfast-partners-with-gotion-high-tech-in-lfp-battery-cell-rd) — VinFast
- [Vietnamese firms dominate green two-wheeler market](https://theinvestor.vn/vietnamese-firms-dominate-green-two-wheeler-market-d16368.html) — The Investor
- [Revised PDP8 under Decision 768](https://kpmg.com/vn/en/home/insights/2025/07/revised-pdp-8.html) — KPMG Vietnam
- [Vietnam Climate Action Tracker](https://climateactiontracker.org/countries/vietnam/) — Climate Action Tracker
- [Vietnam gasoline prices](https://www.globalpetrolprices.com/Vietnam/gasoline_prices/) — GlobalPetrolPrices
- [Promoting the development of electric vehicles in Vietnam](https://theicct.org/wp-content/uploads/2022/12/asia-pacific-evs-promoting-development-evs-vietnam-dec22-2.pdf) — ICCT
- [Electric two-wheeler market growth in Vietnam](https://theicct.org/wp-content/uploads/2022/10/asia-pacific-lvs-NDC-TIA-E2W-mkt-growth-Vietnam-nov22.pdf) — ICCT

---

*Draft prepared March 2026 — Spotlight Data Team, VnExpress*
*Based on IEA LCA Calculator Methodology, adapted for Vietnam market*
