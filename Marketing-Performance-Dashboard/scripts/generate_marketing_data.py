"""
Generate a synthetic multi-channel marketing performance dataset for a
subscription (freemium -> paid) product.

Grain: one row per DAY x CHANNEL x CAMPAIGN x DEVICE.
Window: 2025-01-01 .. 2026-06-30 (18 months) so the dashboard can show
month-over-month trend, seasonality, and a clear efficiency-improvement story.

The full acquisition funnel is modelled end to end so every downstream metric
(CTR, CPC, CPM, CVR, CAC, ROAS, payback, LTV) is internally consistent:

    impressions -> clicks -> sessions -> signups -> trials -> purchases -> revenue

Plus a monthly cohort-retention table for LTV / churn analysis.

Numbers are synthetic but tuned to realistic SaaS/e-commerce economics.
"""

import numpy as np
import pandas as pd
from pathlib import Path

RNG = np.random.default_rng(7)
OUT = Path(__file__).resolve().parents[1] / "data"
OUT.mkdir(parents=True, exist_ok=True)

START = pd.Timestamp("2025-01-01")
END = pd.Timestamp("2026-06-30")
DATES = pd.date_range(START, END, freq="D")

# ---------------------------------------------------------------------------
# Channel economics. Each tuple encodes the "physics" of that channel.
#   base_cpc      : typical cost per click ($)
#   ctr           : click-through rate on impressions
#   sess_rate     : sessions per click (bounce-adjusted)
#   signup_cvr    : signups per session
#   trial_rate    : trials per signup
#   purchase_cvr  : purchases per trial
#   arpu          : average revenue per new customer (first order / first month)
#   quality       : lifetime-value multiplier (retention quality of the cohort)
#   is_paid       : whether spend applies
# ---------------------------------------------------------------------------
CHANNELS = {
    # arpu here = modelled 12-month customer value (LTV), so ROAS reads on annual value.
    "Google Search":   dict(base_cpc=2.40, ctr=0.045, sess_rate=0.92, signup_cvr=0.075, trial_rate=0.55, purchase_cvr=0.42, arpu=380, quality=1.15, is_paid=1, ctype="Paid Search"),
    "Google PMax":     dict(base_cpc=1.35, ctr=0.028, sess_rate=0.85, signup_cvr=0.048, trial_rate=0.50, purchase_cvr=0.36, arpu=300, quality=1.02, is_paid=1, ctype="Paid Search"),
    "Meta Ads":        dict(base_cpc=0.95, ctr=0.021, sess_rate=0.80, signup_cvr=0.040, trial_rate=0.46, purchase_cvr=0.34, arpu=290, quality=0.95, is_paid=1, ctype="Paid Social"),
    "TikTok Ads":      dict(base_cpc=0.62, ctr=0.016, sess_rate=0.72, signup_cvr=0.030, trial_rate=0.40, purchase_cvr=0.26, arpu=165, quality=0.82, is_paid=1, ctype="Paid Social"),
    "LinkedIn Ads":    dict(base_cpc=5.80, ctr=0.011, sess_rate=0.88, signup_cvr=0.055, trial_rate=0.60, purchase_cvr=0.52, arpu=900, quality=1.35, is_paid=1, ctype="Paid Social"),
    "Email":           dict(base_cpc=0.00, ctr=0.180, sess_rate=0.95, signup_cvr=0.090, trial_rate=0.65, purchase_cvr=0.55, arpu=175, quality=1.30, is_paid=0, ctype="Owned"),
    "Organic Search":  dict(base_cpc=0.00, ctr=0.060, sess_rate=0.94, signup_cvr=0.070, trial_rate=0.58, purchase_cvr=0.44, arpu=160, quality=1.20, is_paid=0, ctype="Organic"),
    "Referral":        dict(base_cpc=0.00, ctr=0.140, sess_rate=0.96, signup_cvr=0.110, trial_rate=0.70, purchase_cvr=0.58, arpu=185, quality=1.40, is_paid=0, ctype="Referral"),
}

CAMPAIGNS = {
    "Google Search":  ["Brand", "Non-Brand High Intent", "Competitor Conquest"],
    "Google PMax":    ["PMax - Catalog", "PMax - New Customer"],
    "Meta Ads":       ["Prospecting - Lookalike", "Retargeting - Web", "Advantage+ Shopping"],
    "TikTok Ads":     ["Spark Ads - UGC", "Prospecting - Interest"],
    "LinkedIn Ads":   ["ABM - Enterprise", "Lead Gen - Mid Market"],
    "Email":          ["Lifecycle Nurture", "Winback", "Product Newsletter"],
    "Organic Search": ["SEO - Blog", "SEO - Product Pages"],
    "Referral":       ["Refer-a-Friend", "Partner Program"],
}

DEVICES = ["Mobile", "Desktop", "Tablet"]
DEVICE_MIX = np.array([0.58, 0.36, 0.06])


def seasonality(d: pd.Timestamp) -> float:
    """Multiplicative demand factor: weekly + annual + holiday effects."""
    # Weekday effect (B2C leans to weekends slightly, B2B to weekdays -> mild)
    wk = 1.0 + (0.05 if d.weekday() < 5 else -0.04)
    # Annual growth: the business scales spend/demand ~ +45% over 18 months
    months_in = (d.year - 2025) * 12 + (d.month - 1)
    growth = 1.0 + 0.024 * months_in
    # Q4 holiday spike (Nov/Dec), January "new year" bump, summer softness
    month_factor = {
        1: 1.08, 2: 0.98, 3: 1.02, 4: 1.00, 5: 1.01, 6: 0.96, 7: 0.92,
        8: 0.94, 9: 1.05, 10: 1.10, 11: 1.28, 12: 1.34,
    }[d.month]
    return wk * growth * month_factor


def efficiency(d: pd.Timestamp) -> float:
    """Optimization learning curve: CVR improves ~18% over the window."""
    months_in = (d.year - 2025) * 12 + (d.month - 1)
    return 1.0 + 0.010 * months_in


def generate_fact():
    rows = []
    for d in DATES:
        s = seasonality(d)
        eff = efficiency(d)
        for ch, p in CHANNELS.items():
            # daily spend budget per channel scales with seasonality (paid only)
            base_daily_spend = {
                "Google Search": 1800, "Google PMax": 900, "Meta Ads": 1400,
                "TikTok Ads": 700, "LinkedIn Ads": 1100,
            }.get(ch, 0)
            for camp in CAMPAIGNS[ch]:
                camp_share = RNG.uniform(0.25, 0.5)
                # noise per row
                noise = RNG.normal(1.0, 0.10)

                if p["is_paid"]:
                    spend = base_daily_spend * camp_share * s * noise
                    cpc = p["base_cpc"] * RNG.uniform(0.9, 1.15) / (0.6 + 0.4 * eff)
                    clicks = max(0, spend / cpc)
                    impressions = clicks / max(p["ctr"] * RNG.uniform(0.9, 1.1), 1e-4)
                else:
                    # organic/owned: no spend; volume driven by audience * season
                    base_imps = {
                        "Email": 9000, "Organic Search": 17000, "Referral": 4800,
                    }[ch] * camp_share
                    impressions = base_imps * s * noise
                    clicks = impressions * p["ctr"] * RNG.uniform(0.9, 1.1)
                    spend = 0.0
                    cpc = 0.0

                sessions = clicks * p["sess_rate"] * RNG.uniform(0.95, 1.03)
                signups = sessions * p["signup_cvr"] * eff * RNG.uniform(0.9, 1.1)
                trials = signups * p["trial_rate"] * RNG.uniform(0.92, 1.05)
                purchases = trials * p["purchase_cvr"] * eff * RNG.uniform(0.9, 1.08)
                new_customers = purchases  # 1 purchase = 1 new customer here
                arpu = p["arpu"] * RNG.uniform(0.9, 1.12)
                revenue = new_customers * arpu

                # split across devices
                dev_counts = RNG.multinomial(int(max(sessions, 0)), DEVICE_MIX) if sessions > 0 else [0, 0, 0]
                for dev, frac in zip(DEVICES, DEVICE_MIX):
                    r_spend = spend * frac
                    r_imp = impressions * frac
                    r_clicks = clicks * frac
                    r_sess = sessions * frac
                    r_signups = signups * frac
                    r_trials = trials * frac
                    r_purch = purchases * frac
                    r_cust = new_customers * frac
                    r_rev = revenue * frac
                    rows.append([
                        d.date().isoformat(), ch, p["ctype"], camp, dev,
                        round(r_spend, 2), int(round(r_imp)), int(round(r_clicks)),
                        int(round(r_sess)), int(round(r_signups)), int(round(r_trials)),
                        int(round(r_purch)), int(round(r_cust)), round(r_rev, 2),
                    ])
    cols = ["date", "channel", "channel_type", "campaign", "device",
            "spend", "impressions", "clicks", "sessions", "signups",
            "trials", "purchases", "new_customers", "revenue"]
    df = pd.DataFrame(rows, columns=cols)
    df = df[(df["impressions"] > 0)]  # drop empty device rows
    return df


def generate_cohorts(fact):
    """Monthly acquisition cohorts with a decaying retention curve and expansion."""
    fact = fact.copy()
    fact["date"] = pd.to_datetime(fact["date"])
    fact["cohort_month"] = fact["date"].dt.to_period("M").dt.to_timestamp()
    monthly = (fact.groupby("cohort_month")
               .agg(new_customers=("new_customers", "sum"),
                    m0_revenue=("revenue", "sum"))
               .reset_index())

    rows = []
    max_month = END.to_period("M").to_timestamp()
    for _, c in monthly.iterrows():
        cm = c["cohort_month"]
        n0 = int(c["new_customers"])
        arpu0 = c["m0_revenue"] / max(n0, 1)
        # months observable for this cohort
        months_obs = (max_month.year - cm.year) * 12 + (max_month.month - cm.month)
        for m in range(0, months_obs + 1):
            # retention curve: strong M1 drop, then flattening; better for later cohorts
            base = np.array([1.00, 0.68, 0.57, 0.51, 0.47, 0.44, 0.42, 0.40,
                             0.385, 0.375, 0.368, 0.362, 0.358, 0.355, 0.352,
                             0.350, 0.349, 0.348, 0.347])
            r = base[m] if m < len(base) else base[-1]
            # cohorts later in the window retain a little better (product improved)
            improve = 1.0 + 0.006 * ((cm.year - 2025) * 12 + (cm.month - 1))
            r = min(r * improve, 1.0)
            retained = int(round(n0 * r))
            # revenue per retained customer expands slightly over time (upsell)
            rev_per = arpu0 * (1.0 + 0.03 * m)
            rows.append([
                cm.date().isoformat(), m, n0, retained,
                round(r * 100, 1), round(retained * rev_per, 2),
            ])
    cohorts = pd.DataFrame(rows, columns=[
        "cohort_month", "month_index", "cohort_size", "retained_customers",
        "retention_rate_pct", "cohort_revenue"])
    return cohorts


def main():
    fact = generate_fact()
    fact.to_csv(OUT / "fact_marketing_daily.csv", index=False)

    dim_channel = (pd.DataFrame([
        (ch, p["ctype"], p["base_cpc"], round(p["signup_cvr"] * 100, 2),
         round(p["purchase_cvr"] * 100, 2), p["arpu"], "Paid" if p["is_paid"] else "Free")
        for ch, p in CHANNELS.items()],
        columns=["channel", "channel_type", "benchmark_cpc", "signup_cvr_pct",
                 "trial_to_paid_cvr_pct", "benchmark_arpu", "cost_model"]))
    dim_channel.to_csv(OUT / "dim_channel.csv", index=False)

    cohorts = generate_cohorts(fact)
    cohorts.to_csv(OUT / "cohort_retention.csv", index=False)

    # Monthly channel rollup with derived KPIs (handy for a quick dashboard)
    f = fact.copy()
    f["date"] = pd.to_datetime(f["date"])
    f["month"] = f["date"].dt.to_period("M").dt.to_timestamp().dt.date
    m = (f.groupby(["month", "channel", "channel_type"])
         .agg(spend=("spend", "sum"), impressions=("impressions", "sum"),
              clicks=("clicks", "sum"), sessions=("sessions", "sum"),
              signups=("signups", "sum"), trials=("trials", "sum"),
              purchases=("purchases", "sum"), new_customers=("new_customers", "sum"),
              revenue=("revenue", "sum"))
         .reset_index())
    m["ctr_pct"] = (m["clicks"] / m["impressions"] * 100).round(2)
    m["cpc"] = (m["spend"] / m["clicks"].replace(0, np.nan)).round(2)
    m["cvr_signup_pct"] = (m["signups"] / m["sessions"] * 100).round(2)
    m["cac"] = (m["spend"] / m["new_customers"].replace(0, np.nan)).round(2)
    m["roas"] = (m["revenue"] / m["spend"].replace(0, np.nan)).round(2)
    m.to_csv(OUT / "monthly_channel_summary.csv", index=False)

    # Print a KPI sanity summary
    paid = fact[fact["spend"] > 0]
    total_spend = fact["spend"].sum()
    total_rev = fact["revenue"].sum()
    print("Marketing dataset written to", OUT)
    print(f"  fact_marketing_daily.csv   : {len(fact):,} rows")
    print(f"  monthly_channel_summary.csv: {len(m):,} rows")
    print(f"  cohort_retention.csv       : {len(cohorts):,} rows")
    print("\nHeadline KPIs (full window):")
    print(f"  Total spend    : ${total_spend:,.0f}")
    print(f"  Total revenue  : ${total_rev:,.0f}")
    print(f"  Blended ROAS   : {total_rev/total_spend:,.2f}x")
    print(f"  New customers  : {fact['new_customers'].sum():,.0f}")
    print(f"  Blended CAC    : ${total_spend/max(paid['new_customers'].sum(),1):,.2f}")


if __name__ == "__main__":
    main()
