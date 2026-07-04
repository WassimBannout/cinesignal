"""Unit tests for the pure ETL transforms (PRD §13 Testability, FR-1).

These run in CI without the raw dataset: they exercise the transform functions on
synthetic inputs, which is exactly the correctness surface that matters for FR-1.
"""

import json
import math

import numpy as np
import pandas as pd
import pytest

from pipeline import etl

# --- parse_json_names ---------------------------------------------------------


def test_parse_json_names_extracts_names():
    cell = json.dumps([{"id": 28, "name": "Action"}, {"id": 12, "name": "Adventure"}])
    assert etl.parse_json_names(cell) == ["Action", "Adventure"]


def test_parse_json_names_handles_nan_empty_and_garbage():
    assert etl.parse_json_names(np.nan) == []
    assert etl.parse_json_names("") == []
    assert etl.parse_json_names("not json") == []
    assert etl.parse_json_names(None) == []


def test_parse_json_names_accepts_already_parsed_list():
    assert etl.parse_json_names([{"name": "Drama"}]) == ["Drama"]


def test_parse_json_names_skips_dicts_missing_key():
    cell = json.dumps([{"id": 1}, {"name": "Comedy"}])
    assert etl.parse_json_names(cell) == ["Comedy"]


# --- extract_director ---------------------------------------------------------


def test_extract_director_returns_first_director():
    crew = json.dumps(
        [
            {"job": "Editor", "name": "Someone"},
            {"job": "Director", "name": "Greta Gerwig"},
            {"job": "Director", "name": "Second Director"},
        ]
    )
    assert etl.extract_director(crew) == "Greta Gerwig"


def test_extract_director_none_when_absent_or_bad():
    assert etl.extract_director(json.dumps([{"job": "Writer", "name": "X"}])) is None
    assert etl.extract_director(np.nan) is None
    assert etl.extract_director("garbage") is None


# --- extract_top_cast ---------------------------------------------------------


def test_extract_top_cast_respects_billing_order_and_limit():
    cast = json.dumps([{"name": f"Actor {i}"} for i in range(10)])
    assert etl.extract_top_cast(cast, n=3) == ["Actor 0", "Actor 1", "Actor 2"]


def test_extract_top_cast_handles_missing():
    assert etl.extract_top_cast(np.nan) == []


# --- assign_budget_tier -------------------------------------------------------


@pytest.mark.parametrize(
    "budget,expected",
    [
        (500_000, "micro"),
        (1_000_000, "low"),
        (9_999_999, "low"),
        (10_000_000, "mid"),
        (75_000_000, "high"),
        (250_000_000, "tentpole"),
    ],
)
def test_assign_budget_tier_bands(budget, expected):
    assert etl.assign_budget_tier(budget) == expected


def test_assign_budget_tier_none_for_zero_or_missing():
    assert etl.assign_budget_tier(0) is None
    assert etl.assign_budget_tier(np.nan) is None
    assert etl.assign_budget_tier(None) is None


# --- compute_roi --------------------------------------------------------------


def test_compute_roi_basic():
    assert etl.compute_roi(revenue=300, budget=100) == pytest.approx(2.0)
    assert etl.compute_roi(revenue=50, budget=100) == pytest.approx(-0.5)


# --- clean() integration on a synthetic frame ---------------------------------


@pytest.fixture
def synthetic_raw():
    # `movies` mirrors tmdb_5000_movies.csv (no cast/crew); those live in `credits`
    # and get joined in by clean(). id=2 is duplicated to exercise dedup.
    movies = pd.DataFrame(
        {
            "id": [1, 2, 3, 4, 2],
            "title": ["  Hit ", "Flop", "Unknown Budget", "Tiny", "Flop"],
            "original_title": ["Hit", "Flop", "Unknown Budget", "Tiny", "Flop"],
            "original_language": ["en", "en", "fr", "en", "en"],
            # Realistic magnitudes so valid rows clear MIN_PLAUSIBLE_FINANCIAL.
            # id=3 budget==0 (zero-as-null); id=4 budget==50 (implausibly small).
            "budget": [100_000_000, 200_000_000, 0, 50, 200_000_000],
            "revenue": [300_000_000, 100_000_000, 500_000_000, 200_000_000, 100_000_000],
            "genres": [json.dumps([{"name": "Action"}]), "", "[]", None,
                       json.dumps([{"name": "Action"}])],
            "keywords": ["[]", "[]", "[]", "[]", "[]"],
            "production_countries": [
                json.dumps([{"name": "United States of America"}]),
                json.dumps([{"name": "France"}]),
                "[]", "[]",
                json.dumps([{"name": "United States of America"}]),
            ],
            "production_companies": ["[]", "[]", "[]", "[]", "[]"],
            "release_date": ["2001-05-01", "1999-01-01", "2010-07-07", "2015-03-03", "1999-01-01"],
            "vote_average": [7.5, 5.0, 6.0, 4.0, 5.0],
            "vote_count": [1000, 50, 20, 5, 50],
            "popularity": [10.0, 2.0, 1.0, 0.5, 2.0],
            "runtime": [120, 90, 100, 80, 90],
        }
    )
    # `credits` mirrors tmdb_5000_credits.csv (movie_id ↔ movies.id).
    credits = pd.DataFrame(
        {
            "movie_id": [1, 2, 3, 4],
            "title": ["Hit", "Flop", "Unknown Budget", "Tiny"],
            "cast": [json.dumps([{"name": "Star"}]), "[]", "[]", "[]"],
            "crew": [json.dumps([{"job": "Director", "name": "Dir A"}]), "[]", "[]", "[]"],
        }
    )
    return movies, credits


def test_clean_dedupes_and_derives(synthetic_raw):
    movies, credits = synthetic_raw
    df, report = etl.clean(movies, credits)

    # Duplicate id=2 removed
    assert df["id"].is_unique
    assert len(df) == 4

    # Title whitespace normalised
    assert "Hit" in set(df["title"])

    # ROI computed only where budget>0 and revenue>0
    hit = df[df["id"] == 1].iloc[0]
    assert hit["roi"] == pytest.approx(2.0)
    assert bool(hit["is_profitable"]) is True

    # budget==0 (id=3, zero-as-null) and budget==50 (id=4, implausibly small)
    # → financials invalid, ROI NaN
    unknown = df[df["id"] == 3].iloc[0]
    tiny = df[df["id"] == 4].iloc[0]
    assert unknown["financials_valid"] == False  # noqa: E712
    assert math.isnan(unknown["roi"])
    assert tiny["financials_valid"] == False  # noqa: E712

    # JSON parsed to lists
    assert hit["genres"] == ["Action"]
    assert hit["director"] == "Dir A"
    assert hit["cast_top"] == ["Star"]

    # Report captured the zero-financial accounting
    assert any("budget == 0" in n for n in report.notes)


def test_clean_is_deterministic(synthetic_raw):
    movies, credits = synthetic_raw
    df1, _ = etl.clean(movies.copy(), credits.copy())
    df2, _ = etl.clean(movies.copy(), credits.copy())
    pd.testing.assert_frame_equal(df1, df2)
