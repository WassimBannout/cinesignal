"""Headless app smoke tests (PRD §13 Testability: 'app boots headless in CI').

Uses Streamlit's AppTest to render each view with a real script context and asserts
no uncaught exception — including on a restrictive filter combination, which exercises
the empty-state path (AC-3.5, no crash on empty results).

Skipped automatically if the app extras (streamlit/altair) or the demo Parquet are
absent, so the transform tests still run in a minimal environment.
"""
from __future__ import annotations

import pytest

from pipeline import CLEAN_PARQUET

AppTest = pytest.importorskip("streamlit.testing.v1").AppTest
pytest.importorskip("altair")

pytestmark = pytest.mark.skipif(
    not CLEAN_PARQUET.exists(),
    reason="clean Parquet not present; run `python -m pipeline.etl` first",
)


def _run(view: str) -> AppTest:
    script = (
        "import sys, pathlib\n"
        "sys.path.insert(0, str(pathlib.Path.cwd()))\n"
        f"from app.views import {view}\n"
        f"{view}.render()\n"
    )
    return AppTest.from_string(script, default_timeout=60).run()


@pytest.mark.parametrize("view", ["overview", "profitability", "methodology"])
def test_view_boots_without_exception(view):
    at = _run(view)
    assert not at.exception, [str(e.value) for e in at.exception]


def test_profitability_restrictive_filter_no_crash():
    """A punishing filter must never crash — it shows data or a friendly empty state."""
    at = _run("profitability")
    assert not at.exception, [str(e.value) for e in at.exception]
    # Push the minimum-vote-count slider (last sidebar slider) to its max and re-run.
    at.sidebar.slider[-1].set_value(2000).run()
    assert not at.exception, [str(e.value) for e in at.exception]
