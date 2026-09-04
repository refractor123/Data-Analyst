"""
Generate a synthetic-but-physically-plausible F1 2026 ERS / battery telemetry dataset.

Context: the 2026 F1 power-unit regulations change the electrical side dramatically.
  - MGU-K electrical deployment rises from 120 kW to ~350 kW (~470 hp).
  - The MGU-H is removed; all recovery comes from the MGU-K under braking.
  - Power is split ~50/50 between the internal combustion engine and the electric motor.
  - Cars run on 100% sustainable fuel.
  - A new "Manual Override" deployment mode replaces DRS for overtaking.

This script models a full 24-round 2026 season at LAP LEVEL, producing a small
star schema (one fact table + three dimension tables) suitable for Tableau / Power BI.

Numbers are synthetic and tuned to be internally consistent and physically sensible;
they are NOT official FIA telemetry.
"""

import numpy as np
import pandas as pd
from pathlib import Path

RNG = np.random.default_rng(2026)
OUT = Path(__file__).resolve().parents[1] / "data"
OUT.mkdir(parents=True, exist_ok=True)

# ---------------------------------------------------------------------------
# Dimension: Teams (2026 grid) with a relative power-unit / energy-management rating
# ---------------------------------------------------------------------------
TEAMS = [
    # team, power_unit, pu_rating(0-1 energy mgmt), aero_rating
    ("McLaren",       "Mercedes",     0.94, 0.95),
    ("Ferrari",       "Ferrari",      0.90, 0.90),
    ("Mercedes",      "Mercedes",     0.93, 0.88),
    ("Red Bull",      "Red Bull Ford",0.86, 0.91),
    ("Aston Martin",  "Honda",        0.84, 0.82),
    ("Williams",      "Mercedes",     0.85, 0.80),
    ("Alpine",        "Mercedes",     0.83, 0.78),
    ("Racing Bulls",  "Red Bull Ford",0.82, 0.81),
    ("Haas",          "Ferrari",      0.81, 0.77),
    ("Audi",          "Audi",         0.79, 0.76),
]

# ---------------------------------------------------------------------------
# Dimension: Drivers (two per team)
# ---------------------------------------------------------------------------
DRIVERS = [
    ("Lando Norris",       "McLaren",      4,  0.96),
    ("Oscar Piastri",      "McLaren",      81, 0.95),
    ("Charles Leclerc",    "Ferrari",      16, 0.94),
    ("Lewis Hamilton",     "Ferrari",      44, 0.93),
    ("George Russell",     "Mercedes",     63, 0.93),
    ("Kimi Antonelli",     "Mercedes",     12, 0.87),
    ("Max Verstappen",     "Red Bull",     1,  0.97),
    ("Yuki Tsunoda",       "Red Bull",     22, 0.85),
    ("Fernando Alonso",    "Aston Martin", 14, 0.92),
    ("Lance Stroll",       "Aston Martin", 18, 0.83),
    ("Alex Albon",         "Williams",     23, 0.88),
    ("Carlos Sainz",       "Williams",     55, 0.91),
    ("Pierre Gasly",       "Alpine",       10, 0.87),
    ("Franco Colapinto",   "Alpine",       43, 0.82),
    ("Isack Hadjar",       "Racing Bulls", 6,  0.84),
    ("Liam Lawson",        "Racing Bulls", 30, 0.83),
    ("Esteban Ocon",       "Haas",         31, 0.86),
    ("Oliver Bearman",     "Haas",         87, 0.82),
    ("Nico Hulkenberg",    "Audi",         27, 0.85),
    ("Gabriel Bortoleto",  "Audi",         5,  0.81),
]

# ---------------------------------------------------------------------------
# Dimension: Circuits (2026 calendar) with an energy profile
#   braking_index : how energy-rich the track is for MGU-K harvest (0-1)
#   power_sensitivity : how much lap time rewards electrical deployment (0-1)
# ---------------------------------------------------------------------------
CIRCUITS = [
    # round, gp, country, laps, length_km, base_laptime_s, braking_index, power_sensitivity, night
    (1,  "Australian GP",   "Australia",    58, 5.278, 78.5,  0.62, 0.70, 0),
    (2,  "Chinese GP",      "China",        56, 5.451, 92.0,  0.66, 0.68, 0),
    (3,  "Japanese GP",     "Japan",        53, 5.807, 89.5,  0.55, 0.66, 0),
    (4,  "Bahrain GP",      "Bahrain",      57, 5.412, 91.0,  0.78, 0.72, 1),
    (5,  "Saudi Arabian GP","Saudi Arabia", 50, 6.174, 88.0,  0.58, 0.80, 1),
    (6,  "Miami GP",        "USA",          57, 5.412, 88.5,  0.70, 0.74, 0),
    (7,  "Canadian GP",     "Canada",       70, 4.361, 73.5,  0.90, 0.76, 0),
    (8,  "Monaco GP",       "Monaco",       78, 3.337, 72.5,  0.72, 0.45, 0),
    (9,  "Spanish GP",      "Spain",        66, 4.657, 78.0,  0.60, 0.66, 0),
    (10, "Austrian GP",     "Austria",      71, 4.318, 65.5,  0.80, 0.72, 0),
    (11, "British GP",      "UK",           52, 5.891, 88.0,  0.64, 0.74, 0),
    (12, "Belgian GP",      "Belgium",      44, 7.004, 105.0, 0.58, 0.82, 0),
    (13, "Hungarian GP",    "Hungary",      70, 4.381, 77.0,  0.74, 0.55, 0),
    (14, "Dutch GP",        "Netherlands",  72, 4.259, 71.0,  0.66, 0.60, 0),
    (15, "Italian GP",      "Italy",        53, 5.793, 81.5,  0.50, 0.88, 0),
    (16, "Azerbaijan GP",   "Azerbaijan",   51, 6.003, 102.0, 0.92, 0.84, 0),
    (17, "Singapore GP",    "Singapore",    62, 4.940, 96.0,  0.85, 0.58, 1),
    (18, "United States GP","USA",          56, 5.513, 96.5,  0.72, 0.72, 0),
    (19, "Mexican GP",      "Mexico",       71, 4.304, 78.0,  0.76, 0.70, 0),
    (20, "Brazilian GP",    "Brazil",       71, 4.309, 71.5,  0.78, 0.68, 0),
    (21, "Las Vegas GP",    "USA",          50, 6.201, 95.0,  0.68, 0.86, 1),
    (22, "Qatar GP",        "Qatar",        57, 5.419, 84.0,  0.60, 0.72, 1),
    (23, "Abu Dhabi GP",    "UAE",          58, 5.281, 84.5,  0.70, 0.70, 1),
    (24, "Emilia-Romagna GP","Italy",       63, 4.909, 78.5,  0.64, 0.68, 0),
]

TYRES = ["Soft", "Medium", "Hard"]
WEATHER = ["Dry", "Dry", "Dry", "Dry", "Cloudy", "Cloudy", "Light Rain"]

# 2026 technical constants (modelled)
BATTERY_CAPACITY_MJ = 9.0      # usable energy store per lap deployment budget (modelled)
MAX_DEPLOY_KW = 350            # regulation electrical deployment ceiling
ICE_POWER_KW = 400             # modelled ICE contribution (~50/50 split target)

team_lookup = {t[0]: t for t in TEAMS}


def build_dimensions():
    dim_team = pd.DataFrame(
        [(t[0], t[1], t[2], t[3]) for t in TEAMS],
        columns=["team", "power_unit", "energy_mgmt_rating", "aero_rating"],
    )
    dim_driver = pd.DataFrame(
        [(d[0], d[1], d[2], d[3]) for d in DRIVERS],
        columns=["driver", "team", "car_number", "driver_skill"],
    )
    dim_circuit = pd.DataFrame(
        CIRCUITS,
        columns=["round", "grand_prix", "country", "laps", "length_km",
                 "base_laptime_s", "braking_index", "power_sensitivity", "night_race"],
    )
    dim_circuit["night_race"] = dim_circuit["night_race"].map({0: "Day", 1: "Night"})
    return dim_team, dim_driver, dim_circuit


def generate_fact():
    rows = []
    for (rnd, gp, country, n_laps, length_km, base_lt,
         braking_idx, power_sens, night) in CIRCUITS:
        weather = RNG.choice(WEATHER)
        wet = weather == "Light Rain"
        for driver, team, num, skill in DRIVERS:
            _, pu, pu_rating, aero = team_lookup[team]
            # Each driver's baseline pace this weekend
            car_pace = 0.55 * pu_rating + 0.45 * aero
            weekend_form = RNG.normal(0, 0.35)         # form swing
            reliability_ok = RNG.random() > 0.03       # 3% chance of a PU issue

            # Deployment strategy: how aggressively the driver empties the battery
            aggression = np.clip(RNG.normal(0.72, 0.08) + 0.1 * (skill - 0.85), 0.5, 0.95)

            soc = RNG.uniform(78, 92)                  # start-of-race state of charge %
            start_pos = None
            for lap in range(1, n_laps + 1):
                is_pit = 1 if lap in _pit_laps(n_laps) and RNG.random() > 0.15 else 0

                # --- Energy harvested under braking (MGU-K only in 2026) ---
                harvest = (braking_idx * BATTERY_CAPACITY_MJ
                           * RNG.uniform(0.80, 1.0)
                           * (0.9 + 0.2 * pu_rating))
                if wet:
                    harvest *= RNG.uniform(0.82, 0.95)  # less braking energy, cautious
                harvest = min(harvest, BATTERY_CAPACITY_MJ * 1.05)

                # --- Energy deployed (capped by what's in the store + regs) ---
                # Drivers lift-and-coast when the battery runs low (energy management),
                # so state of charge recovers instead of pinning to the floor.
                low_soc_factor = np.clip((soc - 25) / 40.0, 0.45, 1.0)
                target_deploy = (aggression * low_soc_factor
                                 * BATTERY_CAPACITY_MJ * RNG.uniform(0.9, 1.05))
                available = (soc / 100.0) * BATTERY_CAPACITY_MJ + harvest
                deploy = min(target_deploy, available, BATTERY_CAPACITY_MJ * 1.02)
                deploy = max(deploy, 0.0)

                # Update state of charge (%), keep within battery window
                soc = np.clip(soc + (harvest - deploy) / BATTERY_CAPACITY_MJ * 100
                              + RNG.normal(0, 1.2), 22, 96)

                # Regeneration efficiency (how much braking energy is captured).
                # Driver braking finesse (skill) matters as well as the power unit.
                regen_eff = np.clip(82 + 9 * pu_rating + 14 * (skill - 0.85)
                                    + RNG.normal(0, 1.8) - (4 if wet else 0), 78, 96)

                # Manual Override (2026 overtake mode) deployments this lap
                override = int(RNG.random() < (0.28 * power_sens + 0.05) and not is_pit)

                # Peak electrical power actually used (kW), bounded by 350 regulation
                elec_kw = min(MAX_DEPLOY_KW,
                              MAX_DEPLOY_KW * (0.72 + 0.25 * aggression) * (deploy / BATTERY_CAPACITY_MJ)
                              + (30 if override else 0))
                elec_kw = float(np.clip(elec_kw, 120, MAX_DEPLOY_KW))
                power_split_elec = elec_kw / (elec_kw + ICE_POWER_KW) * 100

                # --- Lap time model ---
                # faster with better car/skill, faster with more deployment on power tracks,
                # slower on pit laps, slower in the wet, low-SoC penalty (can't deploy)
                deploy_gain = power_sens * (deploy / BATTERY_CAPACITY_MJ) * 1.6
                soc_penalty = 0.5 if soc < 30 else 0.0
                lap_time = (base_lt
                            - 1.8 * car_pace - 1.4 * skill - weekend_form
                            - deploy_gain
                            + soc_penalty
                            + (2.6 if wet else 0)
                            + (RNG.uniform(18, 24) if is_pit else 0)
                            + RNG.normal(0, 0.35))
                if lap == 1:
                    lap_time += RNG.uniform(3, 6)      # standing start / first lap traffic

                top_speed = (302 + 34 * power_sens + 0.045 * elec_kw
                             + RNG.normal(0, 3.5) - (12 if wet else 0))

                # crude live position proxy (final position resolved after loop)
                rows.append([
                    rnd, gp, country, "Night" if night else "Day", weather,
                    team, pu, driver, num, lap,
                    round(float(lap_time), 3),
                    round(float(harvest), 3),
                    round(float(deploy), 3),
                    round(float(soc), 1),
                    round(float(regen_eff), 1),
                    override,
                    round(float(elec_kw), 0),
                    round(float(power_split_elec), 1),
                    round(float(top_speed), 1),
                    is_pit,
                    "Wet" if wet else "Slick",
                    round(float(car_pace + skill), 3),
                    int(reliability_ok),
                ])
    cols = ["round", "grand_prix", "country", "day_night", "weather", "team",
            "power_unit", "driver", "car_number", "lap", "lap_time_s",
            "energy_harvested_mj", "energy_deployed_mj", "battery_soc_pct",
            "regen_efficiency_pct", "override_deployments", "electrical_power_kw",
            "electrical_power_split_pct", "top_speed_kmh", "is_pit_lap",
            "tyre_type", "_pace_key", "reliability_ok"]
    df = pd.DataFrame(rows, columns=cols)

    # Resolve finishing position per race from mean clean-lap pace
    clean = df[df["is_pit_lap"] == 0].groupby(["round", "driver"])["lap_time_s"].mean()
    pos = (clean.groupby("round").rank(method="first").astype(int)
           .rename("finish_position").reset_index())
    df = df.merge(pos, on=["round", "driver"], how="left")
    df = df.drop(columns=["_pace_key"])
    return df


def _pit_laps(n_laps):
    # 1-2 stops around thirds of the race
    return {int(n_laps * 0.34), int(n_laps * 0.66)}


def main():
    dim_team, dim_driver, dim_circuit = build_dimensions()
    fact = generate_fact()

    dim_team.to_csv(OUT / "dim_team.csv", index=False)
    dim_driver.to_csv(OUT / "dim_driver.csv", index=False)
    dim_circuit.to_csv(OUT / "dim_circuit.csv", index=False)
    fact.to_csv(OUT / "fact_lap_telemetry.csv", index=False)

    # Race-level rollup (handy single-file table for quick dashboards)
    agg = (fact.groupby(["round", "grand_prix", "country", "day_night", "weather",
                         "team", "power_unit", "driver", "car_number"])
           .agg(laps=("lap", "count"),
                avg_lap_time_s=("lap_time_s", "mean"),
                total_energy_harvested_mj=("energy_harvested_mj", "sum"),
                total_energy_deployed_mj=("energy_deployed_mj", "sum"),
                avg_battery_soc_pct=("battery_soc_pct", "mean"),
                avg_regen_efficiency_pct=("regen_efficiency_pct", "mean"),
                override_deployments=("override_deployments", "sum"),
                avg_electrical_power_kw=("electrical_power_kw", "mean"),
                avg_electrical_split_pct=("electrical_power_split_pct", "mean"),
                max_top_speed_kmh=("top_speed_kmh", "max"),
                finish_position=("finish_position", "first"))
           .reset_index())
    agg["avg_lap_time_s"] = agg["avg_lap_time_s"].round(3)
    for c in ["total_energy_harvested_mj", "total_energy_deployed_mj",
              "avg_battery_soc_pct", "avg_regen_efficiency_pct",
              "avg_electrical_power_kw", "avg_electrical_split_pct"]:
        agg[c] = agg[c].round(2)
    agg.to_csv(OUT / "race_summary.csv", index=False)

    print("F1 dataset written to", OUT)
    print(f"  fact_lap_telemetry.csv : {len(fact):,} rows")
    print(f"  race_summary.csv       : {len(agg):,} rows")
    print(f"  dim tables             : team/driver/circuit")
    print("\nSanity checks:")
    print("  electrical_power_kw max =", fact["electrical_power_kw"].max(), "(reg cap 350)")
    print("  battery_soc_pct range   =", fact["battery_soc_pct"].min(), "-", fact["battery_soc_pct"].max())
    print("  avg electrical split %  =", round(fact["electrical_power_split_pct"].mean(), 1))


if __name__ == "__main__":
    main()
