"""Reusable UI atoms so every view shares one visual language (PRD §10.2).

Convention enforced here: every view opens with a **headline insight sentence** and
every figure carries a plain-language **takeaway** — insight over interaction (§7.3).
"""
from __future__ import annotations

import streamlit as st

# Colour-vision-deficiency-safe accent used consistently across charts.
ACCENT = "#4B8BBE"
BREAKEVEN = "#F63366"


def headline(text: str) -> None:
    """The one-sentence takeaway that opens every view."""
    st.markdown(
        f"<p style='font-size:1.15rem;font-weight:600;line-height:1.4;margin:0 0 .5rem'>"
        f"{text}</p>",
        unsafe_allow_html=True,
    )


def takeaway(text: str) -> None:
    """A 'how to read this' / takeaway line placed under a figure."""
    st.caption(f"📌 {text}")


def caveat(text: str) -> None:
    """A visible correctness caveat (never hide a limitation)."""
    st.warning(text, icon="⚠️")


def footer() -> None:
    """Persistent provenance footer (data vintage + attribution, PRD §10.2)."""
    st.divider()
    st.caption(
        "Data: TMDB 5000 Movie Dataset · vintage ~1916–2017 · nominal USD · US/English-skewed. "
        "This product uses TMDb data but is not endorsed or certified by TMDb. "
        "Built by Wassim Bannout."
    )
