# Build this dashboard in Tableau (free, works on Mac)

Tableau **Public** is free, runs natively on macOS, and publishing gives you a **live shareable link** for your resume / LinkedIn.

## 0. Get the tool
- Download **Tableau Public** (free): https://public.tableau.com/app/discover → create a free account to publish.

## 1. Connect the data
1. **Connect → Text file** → `data/fact_marketing_daily.csv`.
2. Add `cohort_retention.csv` and `dim_channel.csv` as separate data sources (they have a different grain — keep them separate, don't join).
3. Optionally add `monthly_channel_summary.csv` for the pre-computed KPI sheets.

## 2. Calculated fields (on `fact_marketing_daily`)
| Name | Formula |
|---|---|
| ROAS | `SUM([Revenue]) / SUM([Spend])` |
| CAC | `SUM([Spend]) / SUM([New Customers])` |
| CTR % | `SUM([Clicks]) / SUM([Impressions]) * 100` |
| Signup CVR % | `SUM([Signups]) / SUM([Sessions]) * 100` |
| Below Breakeven? | `IF [ROAS] < 1 THEN "Below" ELSE "Profitable" END` |

## 3. Build the sheets
1. **KPI tiles** — `SUM(Revenue)`, `SUM(Spend)`, `ROAS`, `SUM(New Customers)`, `CAC`, `Signup CVR %` as BANs.
2. **Revenue by month** — `MONTH(Date)` (continuous) to Columns, `SUM(Revenue)` to Rows → *Area* mark. Add `SUM(New Customers)` to Tooltip.
3. **ROAS by channel** — `Channel` to Rows, `ROAS` to Columns; filter to paid channels (`Spend > 0`); color by **Below Breakeven?** (blue / red); add a **constant reference line at 1.0**. Sort desc.
4. **CAC by channel** — `Channel` to Rows, `CAC` to Columns; paid only; sort ascending; single orange.
5. **Acquisition funnel** — pivot the funnel columns, or build a bar sheet with the six stage measures (`SUM(Impressions)…SUM(Purchases)`) via *Measure Names/Values*; label with each stage total. (A true funnel look: sort stages, use a descending bar.)
6. **Revenue by channel type** — `Channel Type` to Rows, `SUM(Revenue)` to Columns; color by channel type.
7. **Cohort retention heatmap** — from `cohort_retention.csv`: `Month Index` to Columns, `Cohort Month` to Rows, mark = **Square**, color = `AVG(Retention Rate Pct)` (sequential blue), label = the rate.

## 4. Assemble & publish
- New **Dashboard** (1200px). KPI row on top, then a 2-column grid, cohort heatmap full width at the bottom.
- Dark shading; white/grey text; title *"Multi-Channel Marketing Performance Command Center."*
- Add a `Channel` and a date-range **filter** applied to all worksheets.
- **File → Save to Tableau Public As…** → copy the URL.

### Palette (dark)
`#3987e5` blue (profitable / primary) · `#e66767` red (below breakeven) · `#d95926` orange (CAC) · sequential blue ramp for the heatmap · surface `#1a1a19`.
