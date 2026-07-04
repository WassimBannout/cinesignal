"""CineSignal ETL pipeline.

Turns the raw TMDB 5000 CSVs into one clean, analytical Parquet dataset plus a
data-quality report. See docs/methodology.md for definitions and docs/decisions.md
for the rationale behind each cleaning choice.
"""

from pathlib import Path

# Repo-root-relative paths, resolved once so every module agrees on locations.
ROOT = Path(__file__).resolve().parent.parent
DATA_RAW = ROOT / "data" / "raw"
DATA_PROCESSED = ROOT / "data" / "processed"
REPORTS = ROOT / "reports"

CLEAN_PARQUET = DATA_PROCESSED / "movies_clean.parquet"

__all__ = ["ROOT", "DATA_RAW", "DATA_PROCESSED", "REPORTS", "CLEAN_PARQUET"]
