# DAX measures

All measures live on the `Issues` table in `Detroit311.pbix`. Model: `Issues` is the fact table. `Calendar` (marked as the date table), `Request Type` and `District` are dimensions, each related one to many on `created_date`, `request_category` and `council_district`.

Two helper columns are built in Power Query:

- `closed_in_30d` is 1 when `closed_at` is on or before `created_at` plus 30 days. Open and Archived issues are 0.
- `eligible_30d` is 1 when the issue was created at least 30 days before the newest `created_at` in the data, so every issue in the rate had a full 30 days to close.

Three calculated columns drive the backlog aging page. Age is measured to the newest `created_at` in the data, not to today, so the buckets do not drift. `Age Bucket Order` is the sort key for `Age Bucket`.

```dax
Age Days = INT(MAX(Issues[created_at]) - Issues[created_at])

Age Bucket =
SWITCH(TRUE(),
    Issues[Age Days] <= 7, "0-7 days",
    Issues[Age Days] <= 30, "8-30 days",
    Issues[Age Days] <= 90, "31-90 days",
    "90+ days")

Age Bucket Order =
SWITCH(TRUE(),
    Issues[Age Days] <= 7, 1,
    Issues[Age Days] <= 30, 2,
    Issues[Age Days] <= 90, 3,
    4)
```

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

Two text measures exist only so the cards show full numbers. Power BI abbreviates 209,394 to 209K on a card, and the new card has no display units setting.

```dax
Issues Opened Label = FORMAT([Issues Opened], "#,0")

Open Backlog Label = FORMAT([Open Backlog], "#,0")
```

## Visual scope

`30-Day Close Rate LY` shifts the date filter back one year, so a rate with no date filter compares unlike periods. Four visuals carry their own filter on `Calendar[Month Start]`, on or after 2025-09-01 and before 2026-09-01: the 30-Day Close Rate card, the YoY card, and both matrices on the Where and what page. That is the last 12 cohorts with a full 30 day window, against the 12 before them. The line chart, the other cards, the heat map and the aging page are not filtered by date. The heat map is an Azure Maps visual with its heat map layer on and markers off, filtered to status Open or Acknowledged and latitude above 42, which drops 294 issues whose latitude and longitude are swapped and the issues with no coordinates.

Cross check for the filtered window, from `python src/findings.py`: pandas 0.8478 last 12 months, 0.8858 prior, difference -3.8 points. The cards show 84.8% and -3.8.

## Request type mapping

`docs/request_type_map.csv` maps the 69 raw request types to 15 categories. Power Query joins on the raw text, including the odd characters some names carry. A new raw type in a later pull shows up as a blank category until it is added to the file.

## Opening the file

The report reads `data/issues.parquet` and `docs/request_type_map.csv` through a `RepoFolder` parameter. Change it under Transform data, Edit parameters, to where you cloned the repo.
