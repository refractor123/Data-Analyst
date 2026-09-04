# 📊 Multi-Channel Marketing Performance Command Center

**A full-funnel growth-marketing dashboard that turns $4.0M of spend across 8 channels into a clear budget-reallocation story.**

This project models 18 months of multi-channel marketing — paid, owned and earned — from **impression to purchase to retention**, then surfaces the metrics a growth team actually decides on: **ROAS, CAC, LTV, funnel conversion, and cohort retention.**

> 📊 **[Open the interactive dashboard →](./dashboard.html)** &nbsp;·&nbsp; Built for **Tableau** & **Power BI** (build guides below)

![Marketing Performance Dashboard](./preview.png)

---

## 🎯 What the dashboard shows

- **KPI band** — revenue (12-month customer value), ad spend, blended ROAS, new customers, blended CAC, signup conversion rate.
- **Revenue & new customers by month** — 18-month trend with clear Q4 seasonality.
- **ROAS by channel** — with a 1.0× breakeven line; channels below it lose money.
- **CAC by channel** — cost to acquire a customer, paid channels only.
- **Acquisition funnel** — impression → click → session → signup → trial → purchase, with step conversion.
- **Revenue by channel type** — owned/earned vs paid.
- **Cohort retention heatmap** — % of each month's customers still active N months later.

### Headline findings (the "so what")
- 🟢 **Google Search (2.99×)** and **LinkedIn (2.79×)** are the most efficient paid channels.
- 🔴 **TikTok Ads (0.71×)** is **below breakeven** — the single clearest reallocation opportunity; moving that budget to search/LinkedIn lifts blended ROAS.
- 💌 **Owned & earned** channels (email, organic, referral) drive the **majority of revenue at near-zero CAC**, anchoring a healthy **5.55× blended ROAS**.
- 📉 Retention drops to **~68% at month 1** then flattens around **~35%**, and later cohorts retain a few points better — evidence that product/onboarding improvements are compounding into LTV.

---

## 🗂️ The dataset

Synthetic, modelled to realistic SaaS / e-commerce funnel economics for portfolio demonstration. Generated with Python.

| File | Grain | Rows | Description |
|---|---|---|---|
| `data/fact_marketing_daily.csv` | day × channel × campaign × device | 31k+ | Core funnel fact table |
| `data/monthly_channel_summary.csv` | month × channel | 144 | Pre-computed KPIs (CTR, CPC, CVR, CAC, ROAS) |
| `data/cohort_retention.csv` | cohort month × month index | 171 | Retention curve per acquisition cohort |
| `data/dim_channel.csv` | 8 | — | Channel benchmarks & cost model |

### Data dictionary — `fact_marketing_daily.csv`
| Column | Type | Description |
|---|---|---|
| `date` | date | Day |
| `channel`, `channel_type`, `campaign`, `device` | str | Marketing dimensions |
| `spend` | float | Ad spend ($); 0 for owned/organic/referral |
| `impressions`, `clicks`, `sessions` | int | Top-of-funnel volume |
| `signups`, `trials`, `purchases` | int | Mid/bottom funnel conversions |
| `new_customers` | int | New paying customers |
| `revenue` | float | Attributed 12-month customer value ($) |

### Metrics derived in the dashboard
`CTR = clicks/impressions` · `CPC = spend/clicks` · `Signup CVR = signups/sessions` · `CAC = spend/new_customers` · `ROAS = revenue/spend` · `Retention % = retained/cohort_size`

---

## 🔁 Reproduce it

```bash
pip install pandas numpy
python scripts/generate_marketing_data.py   # build the fact + cohort + dim tables
python scripts/build_aggregates.py           # roll up to dashboard_data.json
python scripts/build_dashboard.py            # inject JSON -> dashboard.html
```

---

## 🛠️ Build guides

- **Tableau (free, Mac-friendly):** [`docs/TABLEAU_GUIDE.md`](./docs/TABLEAU_GUIDE.md)
- **Power BI on Mac (browser):** [`docs/POWERBI_GUIDE.md`](./docs/POWERBI_GUIDE.md)

## 🧰 Skills demonstrated
Marketing analytics · funnel & conversion analysis · ROAS/CAC/LTV modelling · **cohort retention analysis** · data modelling · Python (pandas/numpy) · Tableau · Power BI · GA4-style measurement thinking · turning metrics into budget recommendations.
