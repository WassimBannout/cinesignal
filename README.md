# 🎬 CineSignal — Movie Success Intelligence

**What actually makes a movie successful?** CineSignal answers that question — carefully —
by exploring how a film's **budget, genre, talent, ratings, and box office** relate across
~4,800 films from The Movie Database (TMDB).

It deliberately separates the three things people blur together when they say "success":

- **Revenue** — gross box office
- **Profitability** — ROI = `(revenue − budget) / budget`
- **Reception** — audience ratings

…and never lets one masquerade as another. That distinction is the whole point.

> **Status:** Phase 0 (Foundation & EDA) essentially complete — reproducible ETL +
> data-quality report, a rendered narrative EDA notebook, and a multipage Streamlit app
> (Overview · Profitability · Methodology) all shipped and green in CI. Phase 1 (modeling)
> is next. See the roadmap below.

---

## Why this project exists

CineSignal is a **Data Scientist portfolio project**. It is built to demonstrate the full
arc — *acquire → clean → explore → model → interpret → ship* — with correctness and honesty
as first-class features. Where a design choice trades off "flashy" against "defensible," it
picks defensible: the [Methodology](docs/methodology.md) and [Decisions log](docs/decisions.md)
are part of the product, not an afterthought.

## Three insights (from the [EDA notebook](notebooks/01_eda.ipynb))

1. **Bigger budgets buy revenue, not efficiency.** Budget and revenue rise together
   (log–log Pearson _r_ ≈ 0.62), but budget and **ROI are negatively related**
   (Spearman _ρ_ = −0.14, _p_ ≪ 0.001) — big-budget films return *less* per dollar. Grossing
   high and being profitable are genuinely different things.
2. **The most profitable genres are the cheap ones.** **Horror, Music, and Animation** top
   the table on median ROI (~1.8–2.1×) while **Western, History, and Crime** sit at the
   bottom — and the gap is not chance (Kruskal–Wallis _H_ = 82, _p_ ≪ 0.001).
3. **ROI is wildly skewed, so the median is the only honest headline.** Mean ROI (10.1×) is a
   fiction driven by a few microbudget breakouts; the **median is 1.30×**, and **~76%** of
   films that report financials turn a profit. Timing matters too — summer and holiday
   releases beat September, the industry's "dump month."

> Every figure is reproducible from the committed dataset; see
> [Methodology](docs/methodology.md) for how each number is computed.

---

## Quickstart

```bash
# 1. Environment (Python 3.11+)
python3.12 -m venv .venv && source .venv/bin/activate
pip install -e ".[dev,eda]"          # add ",app,model" as those phases land

# 2. Get the data (one-time manual step — raw data is NOT committed)
#    Download the TMDB 5000 Movie Dataset from Kaggle:
#      https://www.kaggle.com/datasets/tmdb/tmdb-movie-metadata
#    …and place both CSVs in data/raw/ :
#      tmdb_5000_movies.csv, tmdb_5000_credits.csv
python -m pipeline.acquire           # verifies the files are present (fails loudly if not)

# 3. Build the clean dataset + data-quality report
python -m pipeline.etl               # → data/processed/movies_clean.parquet + reports/data_quality.md

# 4. Explore the analysis (narrative EDA notebook, committed rendered)
jupyter lab notebooks/01_eda.ipynb

# 5. Run the app (multipage: Overview · Profitability · Methodology)
pip install -e ".[app]"
streamlit run app/main.py

# 6. Tests + lint
pytest && ruff check pipeline tests app
```

The pipeline is **deterministic** and re-runnable from that single `etl` command. The app
reads the committed demo Parquet, so it boots from a clean clone without re-running the ETL.

## What's in here

```
pipeline/     ETL: acquire (fail-loud data check) · etl (parse, clean, derive, DQ report)
notebooks/    narrative EDA (Phase 0, FR-0) — committed rendered
app/          Streamlit multipage app (Phase 0/1) — Overview, Profitability, …
models/       Success-Score model + interpretation (Phase 1, FR-10)
tests/        unit tests for the pure transforms (run in CI, no raw data needed)
docs/         methodology · data dictionary · decisions log
data/raw/     source CSVs — gitignored, sourced per docs/decisions.md
```

## Data & attribution

Built on the **TMDB 5000 Movie Dataset**. This product uses the TMDb API but is not
endorsed or certified by TMDb; movie data is courtesy of
[The Movie Database](https://www.themoviedb.org). The corpus is historical (~1916–2017) and
**US/English-skewed** — a scope limit we measure and disclose, never paper over. See
[docs/methodology.md](docs/methodology.md).

## Roadmap

| Phase | Theme | Status |
|---|---|---|
| **P0** | Foundation & EDA — ETL, DQ report, EDA notebook, Overview, Profitability, Methodology | ✅ complete |
| **P1** | Modeling & depth — feature engineering, Success-Score model + interpretation, Trends, Critics vs Audience | ⬜ |
| **P2** | Product depth — Movie Deep-Dive, Talent Impact, export/share | ⬜ |
| **P3** | Polish & launch — accessibility, visual refinement, write-up | ⬜ |

## License

[MIT](LICENSE). Data attribution to TMDB honored per its terms.
