"""Pandas versions of the numbers quoted in the README findings."""

from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
OPEN_STATUSES = ["Open", "Acknowledged"]
WINDOW_DAYS = 30
LAST_START = "2025-09-01"
PRIOR_START = "2024-09-01"
END = "2026-09-01"


def close_rate(df, start, end):
    cohort = df[(df["created_at"] >= start) & (df["created_at"] < end)]
    return cohort["closed_in_30d"].mean()


def main():
    df = pd.read_parquet(ROOT / "data" / "issues.parquet")
    types = pd.read_csv(ROOT / "docs" / "request_type_map.csv")
    df = df.merge(types, on="request_type", how="left")

    as_of = df["created_at"].max()
    df["closed_in_30d"] = df["closed_at"] <= df["created_at"] + pd.Timedelta(days=WINDOW_DAYS)
    eligible = df[df["created_at"] <= as_of - pd.Timedelta(days=WINDOW_DAYS)]

    last = close_rate(eligible, LAST_START, END)
    prior = close_rate(eligible, PRIOR_START, LAST_START)
    print(f"last 12 months  {last:.4f}")
    print(f"prior 12 months {prior:.4f}")
    print(f"YoY pts         {(last - prior) * 100:.1f}")

    print("\nby category, last 12 months vs prior 12 months")
    for category in sorted(eligible["category"].unique()):
        rows = eligible[eligible["category"] == category]
        now = close_rate(rows, LAST_START, END)
        before = close_rate(rows, PRIOR_START, LAST_START)
        print(f"{category:32s} {now:.3f} {before:.3f} {(now - before) * 100:+.1f}")

    print("\nopen backlog by age (days since created, as of the newest issue)")
    backlog = df[df["status"].isin(OPEN_STATUSES)].copy()
    backlog["age"] = (as_of - backlog["created_at"]).dt.days
    for label, low, high in [("0-7", 0, 7), ("8-30", 8, 30), ("31-90", 31, 90), ("90+", 91, 10**6)]:
        count = ((backlog["age"] >= low) & (backlog["age"] <= high)).sum()
        print(f"{label:6s} {count}")

    old = backlog[backlog["age"] > 90]
    counts = old["category"].value_counts()
    print(f"\n90+ day backlog {len(old)}")
    for category in counts.index[:3]:
        print(f"{category:32s} {counts[category]}")
    print(f"top 3 share {counts.iloc[:3].sum() / len(old):.3f}")

    print("\n30 day close rate by creation month, first 4 eligible months")
    months = eligible.groupby(eligible["created_at"].dt.to_period("M"))["closed_in_30d"].mean()
    for month in months.index[:4]:
        print(f"{month} {months[month]:.3f}")


if __name__ == "__main__":
    main()
