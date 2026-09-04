# Build this dashboard in Tableau (free, works on Mac)

Tableau **Public** is free and runs natively on macOS. Publishing to Tableau Public gives you a **live, shareable link** — perfect for a resume or LinkedIn.

## 0. Get the tool
- Download **Tableau Public** (free): https://public.tableau.com/app/discover
- Create a free Tableau Public account (needed to publish).

## 1. Connect the data
1. Open Tableau Public → **Connect → Text file** → select `data/fact_lap_telemetry.csv`.
2. Drag `race_summary.csv` and the three `dim_*.csv` files onto the canvas too.
3. Relationships (noodle/drag between tables):
   - `fact_lap_telemetry.driver` → `dim_driver.driver`
   - `fact_lap_telemetry.team` → `dim_team.team`
   - `fact_lap_telemetry.round` → `dim_circuit.round`

> Tip: for speed, most sheets can be built straight off `race_summary.csv`. Use `fact_lap_telemetry.csv` only for the lap-by-lap State-of-Charge line chart.

## 2. Calculated fields (create once, reuse)
| Name | Formula |
|---|---|
| Energy Harvested (GJ) | `SUM([Energy Harvested Mj]) / 1000` |
| Energy Deployed (GJ) | `SUM([Energy Deployed Mj]) / 1000` |
| Avg Regen Efficiency | `AVG([Regen Efficiency Pct])` |
| Peak Electrical Power | `MAX([Electrical Power Kw])` |
| Avg Electric Split % | `AVG([Electrical Power Split Pct])` |

## 3. Build the sheets
1. **KPI tiles** — one sheet per metric: drag the calc to Text, format big. (Or a single row of BANs.)
2. **Energy harvested vs deployed by team** — `Team` to Rows; `Energy Harvested (GJ)` and `Energy Deployed (GJ)` to Columns → *Measure Names* as color for a side-by-side bar. Sort descending.
3. **Regen efficiency leaderboard** — `Driver` to Rows, `Avg Regen Efficiency` to Columns; sort descending; **edit the axis to start near 86%** so the spread is visible. Color by a single blue.
4. **Circuit energy demand** — `Grand Prix` to Rows, `AVG(Energy Harvested Mj)` to Columns; sort descending; color = the same measure (sequential blue). Filter to Top 12.
5. **Battery State of Charge (Bahrain GP)** — from `fact_lap_telemetry`: `Lap` to Columns (continuous), `AVG(Battery Soc Pct)` to Rows, `Driver` to Color. Filter `Grand Prix = Bahrain GP` and filter to 4 drivers.

## 4. Assemble & polish
- New **Dashboard**, size *Automatic* (or 1200px wide). Drag sheets into a KPI row + a 2×2 grid.
- Dark theme: Dashboard → Format → Shading → dark grey; set fonts to white/light grey.
- Add a title: *"Electrifying F1: The 2026 Battery & ERS Revolution."*
- Add a **filter** (e.g. `Team` or `Grand Prix`) and set it to apply to all sheets (*Apply to Worksheets → All Using This Data Source*).

## 5. Publish
- **File → Save to Tableau Public As…** → sign in → done. Copy the public URL for LinkedIn.

### Recommended color palette (dark)
`#199e70` harvested · `#d95926` deployed · `#3987e5` regen/sequential blue · surface `#1a1a19` · text `#ffffff` / `#c3c2b7`.
