# Build this dashboard in Power BI — on a Mac (browser)

Power BI **Desktop is Windows-only**, but you do **not** need it. **Power BI Service** (https://app.powerbi.com) runs entirely in a browser on macOS and can build reports, and **"Publish to web"** gives you a public, embeddable link for LinkedIn.

> You need a **work/school email** to sign up for a free Power BI account (personal Gmail/Outlook aren't accepted by Microsoft). If you don't have one, the **Tableau Public** route (see `TABLEAU_GUIDE.md`) needs no such account.

## 1. Sign in & upload data
1. Go to https://app.powerbi.com → sign in (Fabric/Power BI free tier).
2. **Workspace → New → Upload → your CSVs** (or **New → Semantic model → Excel/CSV**). Upload `race_summary.csv` (fast) and `fact_lap_telemetry.csv`.
3. Create a **report** on top of the uploaded dataset.

## 2. Model (relationships)
In the dataset's **Model view**, link:
- `fact_lap_telemetry[driver]` → `dim_driver[driver]`
- `fact_lap_telemetry[team]` → `dim_team[team]`
- `fact_lap_telemetry[round]` → `dim_circuit[round]`

## 3. DAX measures (New measure)
```DAX
Energy Harvested (GJ) = SUM(fact_lap_telemetry[energy_harvested_mj]) / 1000
Energy Deployed (GJ)  = SUM(fact_lap_telemetry[energy_deployed_mj]) / 1000
Avg Regen Efficiency  = AVERAGE(fact_lap_telemetry[regen_efficiency_pct])
Peak Electrical Power = MAX(fact_lap_telemetry[electrical_power_kw])
Avg Electric Split %  = AVERAGE(fact_lap_telemetry[electrical_power_split_pct])
Override Deployments  = SUM(fact_lap_telemetry[override_deployments])
```

## 4. Visuals
| Visual | Type | Fields |
|---|---|---|
| KPI band | **Card** ×6 | the measures above |
| Harvested vs deployed by team | **Clustered bar** | Axis `team`; Values `Energy Harvested (GJ)`, `Energy Deployed (GJ)` |
| Regen leaderboard | **Clustered bar** | Axis `driver`; Value `Avg Regen Efficiency`; sort desc; format X-axis min ≈ 86 |
| Circuit energy demand | **Clustered bar** | Axis `grand_prix`; Value `AVERAGE(energy_harvested_mj)`; Top-N filter = 12 |
| Battery SoC (Bahrain) | **Line chart** | Axis `lap`; Legend `driver`; Value `AVERAGE(battery_soc_pct)`; page/visual filter `grand_prix = "Bahrain GP"` + 4 drivers |

## 5. Style & publish
- **View → Themes** → pick a dark theme (or Customize theme → paste the palette below).
- Add a text box title and a **slicer** (`team` or `grand_prix`).
- **File → Publish to web (public)** → copy the embed/link for LinkedIn.
  *(If your tenant disables "Publish to web", take a full-screen screenshot instead — the same image used in the README.)*

### Palette (hex, dark)
Harvested `#199E70` · Deployed `#D95926` · Regen/blue `#3987E5` · Background `#1A1A19` · Text `#FFFFFF` / `#C3C2B7`.
