# Build this dashboard in Power BI — on a Mac (browser)

Power BI **Desktop is Windows-only**, but **Power BI Service** (https://app.powerbi.com) runs in any browser on macOS. **"Publish to web"** gives a public link for LinkedIn.

> A **work/school email** is required to create a free Microsoft Power BI account (personal Gmail/Outlook are rejected). No such email? Use the **Tableau Public** route in `TABLEAU_GUIDE.md`.

## 1. Sign in & upload
1. https://app.powerbi.com → sign in → **Workspace → New → Upload** the CSVs.
2. Upload `fact_marketing_daily.csv`, `cohort_retention.csv`, `dim_channel.csv`. Create a **report**.

## 2. DAX measures
```DAX
Total Spend    = SUM(fact_marketing_daily[spend])
Total Revenue  = SUM(fact_marketing_daily[revenue])
ROAS           = DIVIDE([Total Revenue], [Total Spend])
New Customers  = SUM(fact_marketing_daily[new_customers])
CAC            = DIVIDE([Total Spend], [New Customers])
CTR %          = DIVIDE(SUM(fact_marketing_daily[clicks]), SUM(fact_marketing_daily[impressions])) * 100
Signup CVR %   = DIVIDE(SUM(fact_marketing_daily[signups]), SUM(fact_marketing_daily[sessions])) * 100
```

## 3. Visuals
| Visual | Type | Fields |
|---|---|---|
| KPI band | **Card** ×6 | `Total Revenue`, `Total Spend`, `ROAS`, `New Customers`, `CAC`, `Signup CVR %` |
| Revenue by month | **Area / Line** | Axis `date` (by month); Value `Total Revenue` |
| ROAS by channel | **Clustered bar** | Axis `channel`; Value `ROAS`; visual filter `spend > 0`; **analytics → constant line at 1**; conditional format bar color (red if `ROAS < 1`) |
| CAC by channel | **Clustered bar** | Axis `channel`; Value `CAC`; filter `spend > 0`; sort asc |
| Acquisition funnel | **Funnel** | Values = the six stage sums (impressions → purchases) |
| Revenue by channel type | **Clustered bar** | Axis `channel_type`; Value `Total Revenue` |
| Cohort retention | **Matrix** | Rows `cohort_month`; Columns `month_index`; Values `AVG(retention_rate_pct)`; **conditional formatting → Background color** (blue scale) |

## 4. Style & publish
- **View → Themes** → dark theme (or paste the palette below).
- Add a title text box and a `channel` **slicer** + a date slicer.
- **File → Publish to web (public)** → copy the link.
  *(If your tenant blocks Publish to web, use a full-page screenshot — the same one in the README.)*

### Palette (hex)
Blue `#3987E5` (profitable) · Red `#E66767` (below breakeven) · Orange `#D95926` (CAC) · Background `#1A1A19` · Text `#FFFFFF` / `#C3C2B7`.
