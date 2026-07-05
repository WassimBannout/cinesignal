"""CineSignal — app entry point (PRD §14.3).

Streamlit multipage app wired with `st.navigation`. Run from the repo root:

    streamlit run app/main.py

The repo root is put on `sys.path` so the app can import both its own `app.*`
packages and the `pipeline` package (for the clean-dataset location + docs paths).
"""
from __future__ import annotations

import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

import streamlit as st  # noqa: E402

from app.views import methodology, overview, profitability  # noqa: E402

st.set_page_config(page_title="CineSignal", page_icon="🎬", layout="wide")

pages = [
    st.Page(overview.render, title="Overview", icon="🏠", default=True),
    st.Page(profitability.render, title="Profitability", icon="💰"),
    st.Page(methodology.render, title="Methodology & Data", icon="📐"),
]
st.navigation(pages).run()
