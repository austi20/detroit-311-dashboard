"""Pull Improve Detroit 311 issues from the city's ArcGIS layer into data/issues.parquet."""

import logging
import time
from pathlib import Path

import pandas as pd
import requests

LAYER_URL = (
    "https://services2.arcgis.com/qvkbeam7Wirps6zC/arcgis/rest/services/"
    "improve_detroit/FeatureServer/0/query"
)
START_FILTER = "created_at >= TIMESTAMP '2024-07-01 00:00:00'"
PAGE_SIZE = 1000  # layer's maxRecordCount
MAX_RETRIES = 5
DATE_COLUMNS = [
    "created_at",
    "acknowledged_at",
    "updated_at",
    "closed_at",
    "reopened_at",
]
# Archived is neither open nor closed
OPEN_STATUSES = ["Open", "Acknowledged"]
OUT_PATH = Path(__file__).resolve().parent.parent / "data" / "issues.parquet"

log = logging.getLogger("pull")


def fetch_page(offset):
    params = {
        "where": START_FILTER,
        "outFields": "*",
        "orderByFields": "ObjectId",
        "resultOffset": offset,
        "resultRecordCount": PAGE_SIZE,
        "returnGeometry": "false",
        "f": "json",
    }
    for attempt in range(MAX_RETRIES):
        try:
            resp = requests.get(LAYER_URL, params=params, timeout=60)
            resp.raise_for_status()
            body = resp.json()
            # ArcGIS reports errors inside a 200 response
            if "error" in body:
                raise RuntimeError(body["error"])
            return [feature["attributes"] for feature in body["features"]]
        except (requests.RequestException, RuntimeError, ValueError) as err:
            if attempt == MAX_RETRIES - 1:
                raise RuntimeError(
                    f"offset {offset} failed after {MAX_RETRIES} tries"
                ) from err
            wait = 2**attempt
            log.warning("offset %d failed (%s), retrying in %ds", offset, err, wait)
            time.sleep(wait)


def pull_all():
    rows = []
    offset = 0
    while True:
        page = fetch_page(offset)
        rows.extend(page)
        if offset % 20000 == 0:
            log.info("fetched %d rows", len(rows))
        if len(page) < PAGE_SIZE:
            break
        offset += PAGE_SIZE
    return rows


def clean(raw):
    df = raw.copy()
    log.info("raw rows: %d", len(df))

    # epoch ms in UTC, stored as Detroit local time
    for col in DATE_COLUMNS:
        if col in df.columns:
            utc = pd.to_datetime(df[col], unit="ms", utc=True)
            df[col] = utc.dt.tz_convert("America/Detroit").dt.tz_localize(None)

    df = df.drop_duplicates(subset="issue_id")
    log.info("after dropping duplicate issue_id: %d", len(df))

    df = df.dropna(subset=["created_at"])
    log.info("after dropping missing created_at: %d", len(df))

    return df.reset_index(drop=True)


def summarize(df):
    return {
        "rows": len(df),
        "first_created": df["created_at"].min(),
        "last_created": df["created_at"].max(),
        "pct_open": 100 * df["status"].isin(OPEN_STATUSES).mean(),
        "pct_no_closed_at": 100 * df["closed_at"].isna().mean(),
    }


def main():
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    raw = pd.DataFrame(pull_all())
    df = clean(raw)
    OUT_PATH.parent.mkdir(exist_ok=True)
    df.to_parquet(OUT_PATH, index=False)

    s = summarize(df)
    log.info(
        "wrote %s: %d rows, created %s to %s, %.1f%% still open, %.1f%% with no closed_at",
        OUT_PATH.name,
        s["rows"],
        s["first_created"].date(),
        s["last_created"].date(),
        s["pct_open"],
        s["pct_no_closed_at"],
    )


if __name__ == "__main__":
    main()
