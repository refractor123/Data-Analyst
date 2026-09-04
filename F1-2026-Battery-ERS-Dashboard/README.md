# ⚡ Electrifying F1: The 2026 Battery & ERS Revolution

**An analytics deep-dive into how Formula 1's 2026 power-unit regulations turn energy management into the sport's new competitive frontier.**

The 2026 regulations are the biggest technical reset in a decade. This project models a full 24-round season of **lap-level energy-recovery telemetry** and turns it into an interactive dashboard that answers: *who harvests, stores and deploys battery energy best — and where is it won?*

> 📊 **[Open the interactive dashboard →](./dashboard.html)** &nbsp;·&nbsp; Built for **Tableau** & **Power BI** (build guides below)

![F1 2026 Battery & ERS Dashboard](./preview.png)

---

## 🏁 Why this matters — the 2026 rule changes

| Element | 2025 (old) | 2026 (new) | Impact |
|---|---|---|---|
| Electrical deployment (MGU-K) | 120 kW | **350 kW** (+192%) | Electric motor now supplies up to **~47% of peak power** |
| MGU-H (turbo heat recovery) | Yes | **Removed** | All recovery is now under braking (MGU-K only) |
| ICE / electric power split | ~87 / 13 | **~50 / 50** (peak) | Energy strategy decides races |
| Fuel | E10 | **100% sustainable** | Net-zero-carbon fuel |
| Overtaking aid | DRS | **Manual Override Mode** | Battery-boost push-to-pass |

Because the battery now does so much more of the work, **energy recovery efficiency and deployment strategy** become primary performance differentiators — exactly what this dashboard measures.

---

## 📈 What the dashboard shows

- **KPI band** — season energy harvested/deployed (GJ), average regen efficiency, peak electrical power (350 kW cap), average electric power split, and Manual-Override deployments.
- **The deployment leap** — a 2025 → 2026 comparison of electrical power (120 kW → 350 kW).
- **Energy harvested vs deployed by team** — who runs their battery hardest.
- **Energy-recovery efficiency leaderboard** — % of braking energy captured, by driver.
- **Circuit energy demand** — which tracks recover the most energy per lap (heavy-braking street circuits lead).
- **Battery state-of-charge trace** — lap-by-lap SoC for the top finishers at the Bahrain GP, showing the harvest/deploy sawtooth.

### Headline findings
- Heavy-braking street circuits — **Baku, Montreal, Singapore** — recover the most energy per lap (~8 MJ), rewarding aggressive regen setups.
- Top teams convert **~90–92%** of braking energy back into the battery; the midfield trails by 2–3 points, a meaningful lap-time gap under the new rules.
- Deployment routinely **exceeds** harvest per lap, drawing down the store — so **lift-and-coast energy management** is visible in the SoC traces of every car.

---

## 🗂️ The dataset

Synthetic but **physically modelled to the 2026 technical regulations** (350 kW deployment ceiling, MGU-H removed, ~50/50 split, sustainable fuel). Generated with Python. *Not official FIA telemetry.*

A clean **star schema** — one fact table + three dimensions:

| File | Grain | Rows | Description |
|---|---|---|---|
| `data/fact_lap_telemetry.csv` | 1 row / driver / lap | 28,920 | The core telemetry fact table |
| `data/race_summary.csv` | 1 row / driver / race | 480 | Pre-aggregated race rollup (fast dashboards) |
| `data/dim_driver.csv` | 20 | — | Driver, team, car number, skill index |
| `data/dim_team.csv` | 10 | — | Team, power unit, energy-management rating |
| `data/dim_circuit.csv` | 24 | — | 2026 calendar, laps, length, energy profile |

### Data dictionary — `fact_lap_telemetry.csv`
| Column | Type | Description |
|---|---|---|
| `round`, `grand_prix`, `country` | int / str | Race identifiers |
| `day_night`, `weather` | str | Session conditions |
| `team`, `power_unit`, `driver`, `car_number` | str / int | Entrant |
| `lap` | int | Lap number |
| `lap_time_s` | float | Lap time (seconds) |
| `energy_harvested_mj` | float | Energy recovered under braking (MGU-K), MJ |
| `energy_deployed_mj` | float | Battery energy deployed, MJ |
| `battery_soc_pct` | float | Battery state of charge at lap end (%) |
| `regen_efficiency_pct` | float | Share of braking energy captured (%) |
| `override_deployments` | int | Manual-Override (overtake) activations on the lap |
| `electrical_power_kw` | float | Peak electrical power used (≤ 350 kW cap) |
| `electrical_power_split_pct` | float | Electric share of total PU output (%) |
| `top_speed_kmh` | float | Lap top speed |
| `is_pit_lap` | int | 1 if the lap included a pit stop |
| `tyre_type`, `reliability_ok`, `finish_position` | — | Race context |

---

## 🔁 Reproduce it

```bash
pip install pandas numpy
python scripts/generate_f1_data.py     # build the CSV star schema
python scripts/build_aggregates.py     # roll up to dashboard_data.json
python scripts/build_dashboard.py      # inject JSON -> dashboard.html
```

---

## 🛠️ Build guides

- **Tableau (free, Mac-friendly):** [`docs/TABLEAU_GUIDE.md`](./docs/TABLEAU_GUIDE.md)
- **Power BI on Mac (browser):** [`docs/POWERBI_GUIDE.md`](./docs/POWERBI_GUIDE.md)

## 🧰 Skills demonstrated
Data modelling (star schema) · Python (pandas/numpy) · KPI design · energy/physics domain modelling · dashboard design & data visualization · Tableau · Power BI · storytelling with data.
