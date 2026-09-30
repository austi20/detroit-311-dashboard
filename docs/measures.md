# DAX measures

All measures live on the `Issues` table in `Detroit311.pbix`. Model: `Issues` is the fact table. `Calendar` (marked as the date table), `Request Type` and `District` are dimensions, each related one to many on `created_date`, `request_category` and `council_district`.

Two helper columns are built in Power Query:

- `closed_in_30d` is 1 when `closed_at` is on or before `created_at` plus 30 days. Open and Archived issues are 0.
- `eligible_30d` is 1 when the issue was created at least 30 days before the newest `created_at` in the data, so every issue in the rate had a full 30 days to close.

```dax
Issues Opened = COUNTROWS(Issues)

Open Backlog =
CALCULATE(COUNTROWS(Issues), Issues[status] IN {"Open", "Acknowledged"})

Median Days to Close = MEDIAN(Issues[num_days_to_close])

30-Day Close Rate =
VAR Eligible = CALCULATE(COUNTROWS(Issues), Issues[eligible_30d] = 1)
VAR ClosedInWindow =
    CALCULATE(COUNTROWS(Issues), Issues[eligible_30d] = 1, Issues[closed_in_30d] = 1)
RETURN DIVIDE(ClosedInWindow, Eligible)

30-Day Close Rate LY =
CALCULATE([30-Day Close Rate], SAMEPERIODLASTYEAR('Calendar'[Date]))

YoY Δ pts =
VAR ThisYear = [30-Day Close Rate]
VAR LastYear = [30-Day Close Rate LY]
RETURN IF(ISBLANK(ThisYear) || ISBLANK(LastYear), BLANK(), (ThisYear - LastYear) * 100)
```

`Median Days to Close` only sees closed issues, so it is the biased view the 30 day rate is meant to correct. Show them together.

## Cross check against pandas

Cohort month August 2025, data as of 2026-09-28. Pandas values come from `python src/check_measures.py 2025-08`. DAX values come from querying the open model.

| Measure | pandas | DAX |
|---|---:|---:|
| Issues Opened | 9,527 | 9,527 |
| Open Backlog | 22 | 22 |
| Median Days to Close | 9.0 | 9 |
| 30-Day Close Rate | 0.868164 | 0.868164 |
| 30-Day Close Rate LY | 0.553290 | 0.553290 |
| YoY Δ pts | 31.4874 | 31.4874 |

Whole data set: 209,394 rows loaded, 5,068 open (4,687 Acknowledged plus 381 Open), 12,417 issues with no district shown as "Unknown".

## Request type mapping

`docs/request_type_map.csv` maps the 69 raw request types to 15 categories. Power Query joins on the raw text, including the odd characters some names carry. A new raw type in a later pull shows up as a blank category until it is added to the file.

## Opening the file

The report reads `data/issues.parquet` and `docs/request_type_map.csv` through a `RepoFolder` parameter. Change it under Transform data, Edit parameters, to where you cloned the repo.
