"""Pandas numbers quoted in docs/memo.md."""

from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
OPEN_STATUSES = ["Open", "Acknowledged"]
WATCH = ["Grass and Weeds", "Illegal Dumping and Debris"]
LAST_START = "2025-09-01"
PRIOR_START = "2024-09-01"
END = "2026-09-01"


def main():
    df = pd.read_parquet(ROOT / "data" / "issues.parquet")
    types = pd.read_csv(ROOT / "docs" / "request_type_map.csv")
    df = df.merge(types, on="request_type", how="left")
    as_of = df["created_at"].max()
    df["closed_in_30d"] = df["closed_at"] <= df["created_at"] + pd.Timedelta(days=30)
    df["month"] = df["created_at"].dt.to_period("M")
    eligible = df[df["created_at"] <= as_of - pd.Timedelta(days=30)]

    for category in WATCH:
        rows = df[df["category"] == category]
        done = eligible[eligible["category"] == category]
        print(f"\n{category}: issues created and 30 day close rate by month")
        volume = rows.groupby("month").size()
        rate = done.groupby("month")["closed_in_30d"].mean()
        for month in volume.index:
            r = f"{rate[month]:.3f}" if month in rate.index else "  n/a"
            print(f"{month} {volume[month]:6d} {r}")

    backlog = df[df["status"].isin(OPEN_STATUSES)].copy()
    backlog["age"] = (as_of - backlog["created_at"]).dt.days
    old = backlog[backlog["age"] > 90].copy()
    old["council_district"] = old["council_district"].fillna("Unknown").astype(str)
    print(f"\n90+ day backlog {len(old)}, category by district")
    print(pd.crosstab(old["category"], old["council_district"], margins=True).sort_values("All", ascending=False))

    last = eligible[(eligible["created_at"] >= LAST_START) & (eligible["created_at"] < END)].copy()
    prior = eligible[(eligible["created_at"] >= PRIOR_START) & (eligible["created_at"] < LAST_START)].copy()
    for frame in (last, prior):
        frame["council_district"] = frame["council_district"].fillna("Unknown").astype(str)

    print("\ndistrict: 30 day rate last, prior, volume last")
    for d in sorted(last["council_district"].unique()):
        a = last[last["council_district"] == d]
        b = prior[prior["council_district"] == d]
        print(f"D{d:8s} {a['closed_in_30d'].mean():.3f} {b['closed_in_30d'].mean():.3f} {len(a)}")

    print("\nDistrict 4 vs citywide by category (last 12 months): D4 rate, city rate, D4 issues")
    d4 = last[last["council_district"] == "4"]
    for category in sorted(last["category"].unique()):
        a = d4[d4["category"] == category]
        c = last[last["category"] == category]
        if len(a) >= 200:
            print(f"{category:32s} {a['closed_in_30d'].mean():.3f} {c['closed_in_30d'].mean():.3f} {len(a)}")

    print("\nD4 rate if each category closed at the citywide rate")
    expected = 0.0
    for category, n in d4["category"].value_counts().items():
        expected += n * last[last["category"] == category]["closed_in_30d"].mean()
    print(f"expected {expected / len(d4):.3f} actual {d4['closed_in_30d'].mean():.3f}")

    print("\nGrass and Weeds + Illegal Dumping share of slowdown (issues not closed in 30d, last 12m)")
    miss = last[~last["closed_in_30d"]]
    print(len(miss), miss["category"].isin(WATCH).sum())


if __name__ == "__main__":
    main()
