# Detroit 311 Service Performance

![tests](https://github.com/austi20/detroit-311-dashboard/actions/workflows/tests.yml/badge.svg)

How fast does Detroit actually close the service requests residents file through Improve Detroit, and is it getting faster or slower by request type and council district?

The obvious answer, average days to close over closed issues, is biased. Slow issues that are still open drop out of the average, so the city looks faster than it is. I am building a Power BI dashboard around a 30 day close rate by creation month instead, compared with the same months a year earlier. The report pages are in progress. What is here now is the data pipeline and the Power BI model with its measures.

## Data quality

**209,394 issues created June 30, 2024 through September 28, 2026 (pulled September 28, 2026). 2.4% are still open (Open or Acknowledged). 5.1% have no close date, because another 2.7% are Archived without ever being closed.**

| Status | Issues | Share |
|---|---:|---:|
| Closed | 197,605 | 94.4% |
| Archived | 6,721 | 3.2% |
| Acknowledged | 4,687 | 2.2% |
| Open | 381 | 0.2% |

## The data

Source: [Improve Detroit Issues](https://data.detroitmi.gov/datasets/detroitmi::improve-detroit-issues/about), the City of Detroit's open data feed of every non emergency request filed through the Improve Detroit app (potholes, illegal dumping, streetlights, water main leaks). I pull it straight from the city's [ArcGIS REST layer](https://services2.arcgis.com/qvkbeam7Wirps6zC/arcgis/rest/services/improve_detroit/FeatureServer/0), which holds about 753,000 issues back to 2014. I keep everything created on or after July 1, 2024.

Things that were easy to get wrong:

- **Paging.** The layer returns at most 1,000 records per request. `src/pull.py` orders by `ObjectId` and walks `resultOffset` until a page comes back short, with retry and exponential backoff. The full pull is 210 requests and takes about 5 minutes.
- **Errors inside a 200.** ArcGIS reports query errors in the JSON body with HTTP 200, so the script checks for an `error` key instead of trusting the status code.
- **Time zones.** Dates come back as epoch milliseconds in UTC. I convert them to Detroit local time. The server applies the date filter in UTC, which is why 25 issues from the evening of June 30 local time are included.
- **"Open" is not the same as "no close date".** Archived issues have no `closed_at` but are not open either. Treating every missing `closed_at` as open would roughly double the backlog.
- **Reopened issues.** 616 issues have a `reopened_at`. I keep that column. A few reopened issues are back in Open or Acknowledged status while still carrying their old `closed_at`.

Cleaning drops exact duplicate `issue_id`s and rows with no `created_at`, and logs the row count after each step. On this pull neither step removed anything.

The parquet file is not committed. Run the script to rebuild it.

## The model

`Detroit311.pbix` is a star schema. `Issues` is the fact table, with `Calendar` (marked as the date table), `Request Type` and `District` around it. I mapped the 69 raw request types into 15 categories in `docs/request_type_map.csv`. The DAX is in [docs/measures.md](docs/measures.md).

The headline measure is the 30 day close rate by creation month. It only counts issues created at least 30 days before the newest one in the data, so every issue had a full window to close. I also show the median days to close, which only sees closed issues and so runs optimistic.

I checked the measures against pandas for August 2025 (`python src/check_measures.py 2025-08`). All six match: 9,527 issues opened, 22 still open, median 9 days, 30 day close rate 86.8% against 55.3% a year earlier. The 31 point jump is large enough that I want to understand it before I claim the city got faster. It may be a change in how issues were closed in 2024, not in service.

## How to run it

```
pip install -r requirements.txt
python src/pull.py
python -m pytest
```

Open `Detroit311.pbix` and point the `RepoFolder` parameter at your clone (Transform data, Edit parameters).

`pull.py` writes `data/issues.parquet` and logs the summary line above.

## What would break this

- The data records when an issue was marked closed, not whether the problem was fixed.
- 5.9% of issues have no council district, so district level rates will be computed on a slightly smaller set.
- Request types are free text with 69 distinct values in this window, some of them near duplicates. I grouped them by judgment from the names, and a few internal DPW codes land in an Other bucket (8.6% of issues).
- The layer is live. A later pull will not match these counts exactly.
