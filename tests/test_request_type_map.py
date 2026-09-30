from pathlib import Path

import pandas as pd

MAP_PATH = Path(__file__).resolve().parent.parent / "docs" / "request_type_map.csv"


def test_each_raw_type_appears_once():
    mapping = pd.read_csv(MAP_PATH)
    assert not mapping["request_type"].duplicated().any()


def test_category_count_in_range():
    mapping = pd.read_csv(MAP_PATH)
    assert 12 <= mapping["category"].nunique() <= 15


def test_no_blank_categories():
    mapping = pd.read_csv(MAP_PATH)
    assert mapping["category"].notna().all()
