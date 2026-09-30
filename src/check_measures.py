"""Pandas reference values for the Power BI measures, one cohort month."""

import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
OPEN_STATUSES = ["Open", "Acknowledged"]
WINDOW_DAYS = 30


def month_stats(df, month, as_of):
    cohort = df[df["created_at"].dt.to_period("M") == month]
    opened = len(cohort)
    backlog = cohort["status"].isin(OPEN_STATUSES).sum()
    median_days = cohort["num_days_to_close"].median()

    # only cohorts a full window older than the last created issue
    cutoff = as_of - pd.Timedelta(days=WINDOW_DAYS)
    eligible = cohort[cohort["created_at"] <= cutoff]
    closed_in_window = eligible["closed_at"] <= eligible["created_at"] + pd.Timedelta(
        days=WINDOW_DAYS
    )
    rate = closed_in_window.sum() / len(eligible) if len(eligible) else float("nan")
    return opened, backlog, median_days, rate


def main(month_text):
    df = pd.read_parquet(ROOT / "data" / "issues.parquet")
    as_of = df["created_at"].max()
    month = pd.Period(month_text)
    last_year = month - 12

    opened, backlog, median_days, rate = month_stats(df, month, as_of)
    _, _, _, rate_ly = month_stats(df, last_year, as_of)

    print(f"as of {as_of}")
    print(f"month {month}")
    print(f"Issues Opened          {opened}")
    print(f"Open Backlog           {backlog}")
    print(f"Median Days to Close   {median_days}")
    print(f"30-Day Close Rate      {rate:.6f}")
    print(f"30-Day Close Rate LY   {rate_ly:.6f}")
    print(f"YoY pts                {(rate - rate_ly) * 100:.4f}")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "2025-08")
