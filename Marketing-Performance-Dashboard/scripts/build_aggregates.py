"""Roll the marketing daily fact up into the aggregates the HTML dashboard reads."""
import json
from pathlib import Path
import pandas as pd
import numpy as np

BASE = Path(__file__).resolve().parents[1]
DATA = BASE / "data"
fact = pd.read_csv(DATA / "fact_marketing_daily.csv", parse_dates=["date"])
cohort = pd.read_csv(DATA / "cohort_retention.csv")

out = {}

paid = fact[fact["spend"] > 0]
total_spend = fact["spend"].sum()
total_rev = fact["revenue"].sum()

# ---- Headline KPIs -----------------------------------------------------------
out["kpis"] = {
    "spend": round(total_spend, 0),
    "revenue": round(total_rev, 0),
    "roas": round(total_rev / total_spend, 2),
    "new_customers": int(fact["new_customers"].sum()),
    "cac": round(paid["spend"].sum() / max(paid["new_customers"].sum(), 1), 2),
    "signup_cvr": round(fact["signups"].sum() / fact["sessions"].sum() * 100, 2),
    "months": int(fact["date"].dt.to_period("M").nunique()),
}

# ---- Monthly trend: revenue and spend (indexed-friendly, single measure each) -
fact["month"] = fact["date"].dt.to_period("M").dt.to_timestamp()
monthly = (fact.groupby("month")
           .agg(spend=("spend", "sum"), revenue=("revenue", "sum"),
                new_customers=("new_customers", "sum"))
           .reset_index())
monthly["roas"] = (monthly["revenue"] / monthly["spend"]).round(2)
monthly["month"] = monthly["month"].dt.strftime("%Y-%m")
out["monthly"] = monthly.round(0).to_dict(orient="records")

# ---- Channel performance: ROAS, CAC, spend, revenue -------------------------
ch = (fact.groupby(["channel", "channel_type"])
      .agg(spend=("spend", "sum"), revenue=("revenue", "sum"),
           new_customers=("new_customers", "sum"),
           sessions=("sessions", "sum"), signups=("signups", "sum"))
      .reset_index())
ch["roas"] = np.where(ch["spend"] > 0, (ch["revenue"] / ch["spend"]).round(2), None)
ch["cac"] = np.where(ch["spend"] > 0, (ch["spend"] / ch["new_customers"]).round(2), 0.0)
ch["rev_per_customer"] = (ch["revenue"] / ch["new_customers"]).round(2)
ch["signup_cvr"] = (ch["signups"] / ch["sessions"] * 100).round(2)
ch["spend"] = ch["spend"].round(0)
ch["revenue"] = ch["revenue"].round(0)
ch = ch.sort_values("revenue", ascending=False)
out["channels"] = ch.to_dict(orient="records")

# ---- Acquisition funnel (full window totals) --------------------------------
funnel_stages = ["impressions", "clicks", "sessions", "signups", "trials", "purchases"]
labels = ["Impressions", "Clicks", "Sessions", "Signups", "Trials", "Purchases"]
vals = [int(fact[s].sum()) for s in funnel_stages]
out["funnel"] = [{"stage": l, "value": v,
                  "pct_of_top": round(v / vals[0] * 100, 2),
                  "step_cvr": round(v / vals[i - 1] * 100, 1) if i > 0 else 100.0}
                 for i, (l, v) in enumerate(zip(labels, vals))]

# ---- Cohort retention heatmap (cohort_month x month_index) ------------------
piv = cohort.pivot(index="cohort_month", columns="month_index",
                   values="retention_rate_pct")
out["cohort"] = {
    "cohorts": [c[:7] for c in piv.index.tolist()],
    "months": [int(m) for m in piv.columns.tolist()],
    "matrix": [[None if pd.isna(v) else round(float(v), 1) for v in row]
               for row in piv.values.tolist()],
}

# ---- Spend vs revenue mix by channel type -----------------------------------
mix = (fact.groupby("channel_type")
       .agg(spend=("spend", "sum"), revenue=("revenue", "sum"),
            new_customers=("new_customers", "sum"))
       .reset_index().sort_values("revenue", ascending=False))
mix["spend"] = mix["spend"].round(0)
mix["revenue"] = mix["revenue"].round(0)
out["channel_type_mix"] = mix.to_dict(orient="records")

(Path(DATA) / "dashboard_data.json").write_text(json.dumps(out, indent=1))
print("Marketing aggregates ->", DATA / "dashboard_data.json")
print("  channels:", len(out["channels"]), "| months:", len(out["monthly"]),
      "| cohorts:", len(out["cohort"]["cohorts"]))
