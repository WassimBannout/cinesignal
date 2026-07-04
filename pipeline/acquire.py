"""Data acquisition step for CineSignal (PRD FR-1, §12).

The raw data is **never committed** to git (PRD §12.0). This module is the single,
documented, reproducible entry point that locates the raw TMDB 5000 CSVs and
**fails loudly with clear instructions** if they are absent.

Chosen source (OQ8 → resolved): the *TMDB 5000 Movie Dataset* on Kaggle:
    https://www.kaggle.com/datasets/tmdb/tmdb-movie-metadata

It ships as two files that the ETL will join itself (a deliberate ETL signal):
    - tmdb_5000_movies.csv    (financials + reception + content)
    - tmdb_5000_credits.csv   (cast + crew → talent)

Because Kaggle downloads require authentication, acquisition is a *documented
manual step* rather than an unattended fetch — this keeps the pipeline
credential-free and deterministic. Run this module to verify the files are in
place before running the ETL.
"""

from __future__ import annotations

import sys
from dataclasses import dataclass

from pipeline import DATA_RAW

# Expected raw inputs and the columns the ETL relies on. Keeping the expectation
# here (not buried in the ETL) lets acquisition fail early and legibly.
MOVIES_CSV = "tmdb_5000_movies.csv"
CREDITS_CSV = "tmdb_5000_credits.csv"

REQUIRED_FILES = (MOVIES_CSV, CREDITS_CSV)

KAGGLE_URL = "https://www.kaggle.com/datasets/tmdb/tmdb-movie-metadata"


@dataclass(frozen=True)
class Acquisition:
    """Resolved, verified locations of the raw inputs."""

    movies_path: str
    credits_path: str


def _instructions() -> str:
    return (
        f"\nRaw data not found. CineSignal does not commit raw data to git (PRD §12.0).\n"
        f"To obtain it (one-time manual step):\n\n"
        f"  1. Download the TMDB 5000 Movie Dataset from:\n"
        f"       {KAGGLE_URL}\n"
        f"     (Kaggle login required; or use the Kaggle CLI:\n"
        f"       kaggle datasets download -d tmdb/tmdb-movie-metadata -p data/raw --unzip )\n\n"
        f"  2. Place these two files in:  {DATA_RAW}/\n"
        f"       - {MOVIES_CSV}\n"
        f"       - {CREDITS_CSV}\n\n"
        f"  3. Re-run:  python -m pipeline.acquire\n"
    )


def resolve() -> Acquisition:
    """Verify the raw files exist; raise FileNotFoundError with instructions if not."""
    missing = [name for name in REQUIRED_FILES if not (DATA_RAW / name).is_file()]
    if missing:
        raise FileNotFoundError(
            f"Missing raw file(s): {', '.join(missing)}\n{_instructions()}"
        )
    return Acquisition(
        movies_path=str(DATA_RAW / MOVIES_CSV),
        credits_path=str(DATA_RAW / CREDITS_CSV),
    )


def main() -> int:
    """CLI entry point: verify raw data is present and report where."""
    try:
        acq = resolve()
    except FileNotFoundError as exc:
        print(str(exc), file=sys.stderr)
        return 1
    print("✓ Raw data located:")
    print(f"    movies : {acq.movies_path}")
    print(f"    credits: {acq.credits_path}")
    print("\nNext: python -m pipeline.etl")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
