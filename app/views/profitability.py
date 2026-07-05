"""Profitability explorer (FR-3) — return on investment, not just gross.

AC-3.1 ROI formula visible · AC-3.2 filters (year/genre/tier/min votes) ·
AC-3.3 ROI *distribution* per genre (box) · AC-3.4 multi-genre caveat ·
AC-3.5 friendly empty state (never a crash).
"""
from __future__ import annotations

import altair as alt
import streamlit as st

from app.components import ui
from app.components.data import (
    BUDGET_TIER_ORDER,
    MIN_GENRE_FILMS,
    all_genres,
    genre_exploded,
    load_data,
)


def render() -> None:
    df = load_data()
    fin = df[df.financials_valid].copy()

    st.title("💰 Profitability")
    st.markdown(
        "Return on investment: "
        r"$\mathrm{ROI} = (\text{revenue} - \text{budget}) \,/\, \text{budget}$. "
        "An ROI of **1.0×** means the film earned back its budget again on top of covering it."
    )

    # --- Filters (AC-3.2) -----------------------------------------------------
    genres = all_genres(df)
    yr_lo, yr_hi = int(fin.release_year.min()), int(fin.release_year.max())
    with st.sidebar:
        st.header("Filters")
        year_range = st.slider("Release year", yr_lo, yr_hi, (yr_lo, yr_hi))
        picked_genres = st.multiselect("Genres", genres, default=[])
        tiers = st.multiselect("Budget tier", BUDGET_TIER_ORDER, default=[])
        min_votes = st.slider(
            "Minimum vote count", 0, 2000, 0, step=50,
            help="Exclude low-vote films whose scores/financials are noisier.",
        )

    # --- Apply filters --------------------------------------------------------
    mask = fin.release_year.between(*year_range) & (fin.vote_count >= min_votes)
    if tiers:
        mask &= fin.budget_tier.isin(tiers)
    sub = fin[mask]

    g = genre_exploded(sub)
    counts = g.genres.value_counts()
    eligible = counts[counts >= MIN_GENRE_FILMS].index
    g = g[g.genres.isin(eligible)]
    if picked_genres:
        g = g[g.genres.isin(picked_genres)]

    # --- Empty state (AC-3.5) -------------------------------------------------
    if g.empty:
        ui.headline("No films match these filters.")
        st.info(
            "Try widening the year range, clearing the budget-tier or genre selection, "
            "or lowering the minimum vote count. "
            f"(Genres need ≥ {MIN_GENRE_FILMS} films to be shown.)"
        )
        ui.footer()
        return

    order = g.groupby("genres").roi.median().sort_values(ascending=False).index.tolist()
    best = order[0]
    ui.headline(
        f"Among the current selection, **{best}** returns the most per dollar "
        f"(median ROI {g[g.genres == best].roi.median():.2f}×)."
    )

    # --- ROI distribution per genre (AC-3.3) — distribution, not just a mean ---
    box = (
        alt.Chart(g)
        .mark_boxplot(extent=1.5, outliers=False, color=ui.ACCENT)
        .encode(
            x=alt.X("roi:Q", title="ROI = (revenue − budget) / budget",
                    scale=alt.Scale(domain=[-2, 8], clamp=True)),
            y=alt.Y("genres:N", sort=order, title=None),
            tooltip=[alt.Tooltip("genres:N")],
        )
        .properties(height=max(220, 26 * len(order)))
    )
    st.altair_chart(box, width="stretch")
    ui.takeaway(
        "Boxes show the middle 50% of each genre's ROI; the line is the median. "
        "Whiskers/outliers beyond 8× are clipped for legibility — ROI is heavy-tailed, "
        "which is exactly why we compare medians, not means."
    )

    # --- Summary table (AC-3.3) -----------------------------------------------
    table = (
        g.groupby("genres")
        .agg(
            films=("roi", "count"),
            median_ROI=("roi", "median"),
            pct_profitable=("is_profitable", "mean"),
            median_revenue=("revenue", "median"),
        )
        .reindex(order)
    )
    st.dataframe(
        table.style.format(
            {
                "median_ROI": "{:.2f}×",
                "pct_profitable": "{:.0%}",
                "median_revenue": "${:,.0f}",
            }
        ),
        width="stretch",
    )

    # --- Multi-genre caveat (AC-3.4) ------------------------------------------
    ui.caveat(
        "**Multi-genre attribution:** a film with several genres is counted once in *each* "
        "of its genres, so genre groups overlap. This is why we never *sum* a metric across "
        "genres (that would double-count) — only compare per-genre medians and distributions."
    )

    ui.footer()
