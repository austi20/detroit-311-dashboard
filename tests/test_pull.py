import pandas as pd

import pull


def make_raw():
    # epoch ms, as the ArcGIS layer returns them
    return pd.DataFrame(
        {
            "issue_id": [1.0, 2.0, 2.0, 3.0, 4.0],
            "status": ["Closed", "Open", "Open", "Acknowledged", "Archived"],
            "created_at": [
                1719835200000,
                1719921600000,
                1719921600000,
                1720008000000,
                1720008000000,
            ],
            "closed_at": [1720008000000, None, None, None, None],
            "reopened_at": [None, None, None, 1720094400000, None],
        }
    )


def test_clean_converts_epoch_ms_to_datetimes():
    df = pull.clean(make_raw())
    assert pd.api.types.is_datetime64_any_dtype(df["created_at"])
    assert df.loc[df["issue_id"] == 1, "created_at"].iloc[0] == pd.Timestamp(
        "2024-07-01 08:00:00"
    )


def test_clean_drops_duplicate_issue_ids_and_keeps_reopened():
    df = pull.clean(make_raw())
    assert len(df) == 4
    assert df["issue_id"].is_unique
    assert df["reopened_at"].notna().sum() == 1


def test_clean_leaves_open_issues_without_closed_at():
    df = pull.clean(make_raw())
    assert df["closed_at"].isna().sum() == 3


def test_pull_all_pages_until_short_page(monkeypatch):
    offsets = []

    def fake_fetch_page(offset):
        offsets.append(offset)
        size = pull.PAGE_SIZE if offset < 2 * pull.PAGE_SIZE else 5
        return [{"issue_id": offset + i} for i in range(size)]

    monkeypatch.setattr(pull, "fetch_page", fake_fetch_page)
    rows = pull.pull_all()
    assert offsets == [0, pull.PAGE_SIZE, 2 * pull.PAGE_SIZE]
    assert len(rows) == 2 * pull.PAGE_SIZE + 5


def test_summarize_reports_rows_range_and_share_open():
    summary = pull.summarize(pull.clean(make_raw()))
    assert summary["rows"] == 4
    assert summary["first_created"] == pd.Timestamp("2024-07-01 08:00:00")
    # archived without a close date is not open
    assert summary["pct_open"] == 50.0
    assert summary["pct_no_closed_at"] == 75.0
