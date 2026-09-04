"""Roll the F1 lap telemetry up into the small aggregates the HTML dashboard reads."""
import json
from pathlib import Path
import pandas as pd

BASE = Path(__file__).resolve().parents[1]
DATA = BASE / "data"
fact = pd.read_csv(DATA / "fact_lap_telemetry.csv")
race = pd.read_csv(DATA / "race_summary.csv")

out = {}

# ---- Headline KPIs -----------------------------------------------------------
out["kpis"] = {
    "total_harvested_gj": round(fact["energy_harvested_mj"].sum() / 1000, 1),   # MJ -> GJ
    "total_deployed_gj": round(fact["energy_deployed_mj"].sum() / 1000, 1),
    "avg_regen_eff": round(fact["regen_efficiency_pct"].mean(), 1),
    "peak_power_kw": int(fact["electrical_power_kw"].max()),
    "avg_elec_split": round(fact["electrical_power_split_pct"].mean(), 1),
    "override_total": int(fact["override_deployments"].sum()),
    "races": int(fact["round"].nunique()),
    "laps": int(len(fact)),
}

# ---- Energy harvested vs deployed by team -----------------------------------
team = (fact.groupby("team")
        .agg(harvested=("energy_harvested_mj", "sum"),
             deployed=("energy_deployed_mj", "sum"),
             regen=("regen_efficiency_pct", "mean"))
        .reset_index())
team["harvested"] = (team["harvested"] / 1000).round(1)   # GJ
team["deployed"] = (team["deployed"] / 1000).round(1)
team["regen"] = team["regen"].round(1)
team = team.sort_values("harvested", ascending=False)
out["team_energy"] = team.to_dict(orient="records")

# ---- Regen efficiency leaderboard by driver (top 12) ------------------------
drv = (fact.groupby(["driver", "team"])
       .agg(regen=("regen_efficiency_pct", "mean"),
            harvested=("energy_harvested_mj", "sum"))
       .reset_index())
drv["regen"] = drv["regen"].round(1)
drv["harvested"] = (drv["harvested"] / 1000).round(1)
drv = drv.sort_values("regen", ascending=False).head(12)
out["driver_regen"] = drv.to_dict(orient="records")

# ---- Circuit energy demand (total harvest per circuit, per-car average) -----
circ = (fact.groupby(["round", "grand_prix"])
        .agg(harvest_per_lap=("energy_harvested_mj", "mean"),
             deploy_per_lap=("energy_deployed_mj", "mean"))
        .reset_index()
        .sort_values("harvest_per_lap", ascending=False))
circ["harvest_per_lap"] = circ["harvest_per_lap"].round(2)
circ["deploy_per_lap"] = circ["deploy_per_lap"].round(2)
out["circuit_demand"] = circ.to_dict(orient="records")

# ---- Battery State of Charge trace over one race (Bahrain) -------------------
# Pick four fast, well-managed cars whose SoC stays in a healthy operating band
# (a nice harvest/deploy sawtooth rather than a drained flat line).
bahrain = fact[fact["grand_prix"] == "Bahrain GP"].copy()
soc_stats = (bahrain.groupby("driver")
             .agg(min_soc=("battery_soc_pct", "min"),
                  mean_soc=("battery_soc_pct", "mean"),
                  pace=("lap_time_s", "mean")))
healthy = soc_stats[soc_stats["min_soc"] >= 45].sort_values("pace")
picks = (healthy.index.tolist() or soc_stats.sort_values("pace").index.tolist())[:4]
soc_series = []
for d in picks:
    dd = bahrain[bahrain["driver"] == d].sort_values("lap")
    soc_series.append({
        "driver": d,
        "team": dd["team"].iloc[0],
        "points": [{"lap": int(l), "soc": float(s)}
                   for l, s in zip(dd["lap"], dd["battery_soc_pct"])],
    })
out["soc_trace"] = {"grand_prix": "Bahrain GP", "series": soc_series}

# ---- Deployment vs pace: team avg deployed/lap vs avg clean lap time ---------
clean = fact[fact["is_pit_lap"] == 0]
scatter = (clean.groupby("team")
           .agg(deploy=("energy_deployed_mj", "mean"),
                laptime=("lap_time_s", "mean"),
                power=("electrical_power_kw", "mean"))
           .reset_index())
scatter["deploy"] = scatter["deploy"].round(2)
scatter["laptime"] = scatter["laptime"].round(2)
scatter["power"] = scatter["power"].round(0)
out["deploy_pace"] = scatter.to_dict(orient="records")

(Path(DATA) / "dashboard_data.json").write_text(json.dumps(out, indent=1))
print("F1 aggregates ->", DATA / "dashboard_data.json")
print("  teams:", len(out["team_energy"]), "| circuits:", len(out["circuit_demand"]),
      "| soc drivers:", len(out["soc_trace"]["series"]))
