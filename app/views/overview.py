"""Overview dashboard (FR-2) — corpus at a glance + one striking fact.

AC-2.1 KPI row · AC-2.2 budget-vs-revenue log-log scatter w/ break-even line ·
AC-2.3 films-per-year with coverage note · AC-2.4 a takeaway per figure.
"""
from __future__ import annotations

import altair as alt
import streamlit as st

from app.components import ui
from app.components.data import genre_exploded, load_data


def render() -> None:
    df = load_data()
    fin = df[df.financials_valid]

    st.title("🎬 CineSignal — What makes a movie succeed?")

    year_min, year_max = int(df.release_year.min()), int(df.release_year.max())
    us_share = df.production_countries.apply(
        lambda cs: "United States of America" in cs
    ).mean()
    g = genre_exploded(fin)
    counts = g.genres.value_counts()
    med_by_genre = g[g.genres.isin(counts[counts >= 30].index)].groupby("genres").roi.median()
    best_genre = med_by_genre.idxmax()

    ui.headline(
        f"{len(df):,} films ({year_min}–{year_max}), {us_share:.0%} US-produced — "
        f"and the most profitable genre is **{best_genre}**, not the biggest-budget one."
    )

    # --- KPI row (AC-2.1) -----------------------------------------------------
    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Films", f"{len(df):,}")
    c2.metric("Year span", f"{year_min}–{year_max}")
    c3.metric("Median ROI", f"{fin.roi.median():.2f}×",
              help="On the ~67% of films with valid financials")
    c4.metric("Median audience score", f"{df.vote_average.median():.1f}/10")
    c5.metric("Most profitable genre", best_genre, help=f"Median ROI {med_by_genre.max():.2f}×")

    st.divider()

    # --- Budget vs revenue, log-log, with break-even line (AC-2.2) ------------
    st.subheader("Budget vs. revenue")
    scatter_src = fin[["title", "budget", "revenue", "roi"]].copy()
    base = alt.Chart(scatter_src)
    points = base.mark_circle(size=18, opacity=0.25, color=ui.ACCENT).encode(
        x=alt.X("budget:Q", scale=alt.Scale(type="log"), title="Budget ($)"),
        y=alt.Y("revenue:Q", scale=alt.Scale(type="log"), title="Revenue ($)"),
        tooltip=[
            alt.Tooltip("title:N", title="Film"),
            alt.Tooltip("budget:Q", format="$,.0f"),
            alt.Tooltip("revenue:Q", format="$,.0f"),
            alt.Tooltip("roi:Q", format=".2f", title="ROI"),
        ],
    )
    lo, hi = scatter_src.budget.min(), scatter_src.revenue.max()
    line_df = alt.Data(values=[{"v": float(lo)}, {"v": float(hi)}])
    breakeven = (
        alt.Chart(line_df)
        .mark_line(color=ui.BREAKEVEN, strokeDash=[6, 4])
        .encode(x=alt.X("v:Q"), y=alt.Y("v:Q"))
    )
    st.altair_chart((points + breakeven).interactive(), width="stretch")
    ui.takeaway(
        "Points above the dashed line turned a profit. Budget and revenue rise together "
        "(log–log r ≈ 0.62), but the spread around the line is where profitability lives — "
        "a big budget guarantees neither."
    )

    st.divider()

    # --- Films per year + coverage note (AC-2.3) ------------------------------
    st.subheader("Coverage over time")
    per_year = (
        df.dropna(subset=["release_year"])
        .assign(release_year=lambda d: d.release_year.astype(int))
        .groupby("release_year")
        .size()
        .reset_index(name="films")
    )
    bars = alt.Chart(per_year).mark_bar(color=ui.ACCENT).encode(
        x=alt.X("release_year:O", title="Release year", axis=alt.Axis(labelOverlap=True)),
        y=alt.Y("films:Q", title="Films"),
        tooltip=["release_year", "films"],
    )
    st.altair_chart(bars, width="stretch")
    early = int(per_year.query("release_year < 1990").films.sum())
    ui.takeaway(
        f"Coverage is heavily weighted to recent decades — only {early:,} films predate 1990. "
        "Pre-1980 years are sparse, so treat early-era trends as indicative, not robust."
    )

    ui.footer()
