"""Cached data access for the app (PRD §13 Performance: cached load).

Every view reads the *same* clean Parquet the ETL produced — the app never re-derives
metrics, so a number on screen always traces back to `pipeline/etl.py`.
"""
from __future__ import annotations

import numpy as np
import pandas as pd
import streamlit as st

from pipeline import CLEAN_PARQUET

# Documented genre-inclusion threshold: below this many ROI-computable films a genre
# is too small to summarise honestly (matches the EDA notebook, §5).
MIN_GENRE_FILMS = 30

BUDGET_TIER_ORDER = ["micro", "low", "mid", "high", "tentpole"]


def _as_list(value: object) -> list:
    """Parquet returns list columns as numpy arrays; normalise to plain lists."""
    if isinstance(value, np.ndarray):
        return value.tolist()
    if isinstance(value, list):
        return value
    return []


@st.cache_data(show_spinner="Loading CineSignal data…")
def load_data() -> pd.DataFrame:
    """Load the clean dataset once and cache it for the session.

    Raises a clear Streamlit error (rather than a stack trace) if the Parquet is
    missing — the fix is to run the pipeline first.
    """
    if not CLEAN_PARQUET.exists():
        st.error(
            "Clean dataset not found. Build it first:\n\n"
            "```\npython -m pipeline.acquire   # verify raw CSVs are present\n"
            "python -m pipeline.etl       # → data/processed/movies_clean.parquet\n```"
        )
        st.stop()
    df = pd.read_parquet(CLEAN_PARQUET)
    for col in ("genres", "keywords", "production_countries", "cast_top"):
        if col in df.columns:
            df[col] = df[col].apply(_as_list)
    return df


def genre_exploded(df: pd.DataFrame) -> pd.DataFrame:
    """One row per (film, genre) — for genre-level analysis without double-counting sums.

    Not cached: list columns aren't hashable as a cache key, and exploding a few
    thousand rows is cheap. `load_data` (the expensive read) is what we cache.
    """
    return df.explode("genres").dropna(subset=["genres"])


def all_genres(df: pd.DataFrame) -> list[str]:
    """Sorted list of genres that clear the minimum-films threshold on the ROI subset."""
    g = genre_exploded(df[df.financials_valid])
    counts = g.genres.value_counts()
    return sorted(counts[counts >= MIN_GENRE_FILMS].index.tolist())
