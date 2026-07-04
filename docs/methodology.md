# Methodology & Data Quality

> This document backs the in-app **Methodology page (FR-7)** — a first-class feature, not
> fine print (PRD §3, §11.7). It is written for a technical reviewer. Sections marked
> _(pending)_ are filled as later phases ship.

## 1. Data source & vintage

- **Source:** TMDB 5000 Movie Dataset (`tmdb_5000_movies.csv`, `tmdb_5000_credits.csv`).
- **Vintage:** historical corpus spanning roughly **1916–2017**. Financial figures are
  **nominal USD** (not inflation-adjusted); some fields (e.g. popularity) are era-specific.
- **Attribution:** "This product uses the TMDb API but is not endorsed or certified by
  TMDb." Movie data courtesy of The Movie Database (themoviedb.org).

## 2. Known biases & scope limits (AC-7.1)

- **Geographic/language skew:** the corpus is **US/English-dominant**. The exact share is
  measured by the pipeline and reported in `reports/data_quality.md`; the app states the
  limit rather than implying generality.
- **Non-random missingness:** films lacking budget/revenue skew indie/foreign, so the
  ROI-analysis subset is not a random sample of all films (see D2 in `decisions.md`).
- **No critic score:** TMDB provides only an audience score. A true Critics-vs-Audience
  analysis (FR-5) requires an IMDB `title.ratings` enrichment _(pending)_.

## 3. Cleaning decisions (AC-7.2)

Full rationale in [`decisions.md`](decisions.md); kept/dropped counts are auto-generated in
[`../reports/data_quality.md`](../reports/data_quality.md) each pipeline run. Summary:

| Decision | Rule | Ref |
|---|---|---|
| Zeros as nulls | `budget==0` or `revenue==0` → missing; excluded from ROI | D2 |
| Implausible financials | non-zero value `< $1,000` → excluded from ROI | D3 |
| Dedup | drop duplicate `id` rows | D5 |
| Nested JSON | genres/keywords/companies/countries parsed to lists | AC-1.2 |
| Talent | director from crew (`job == "Director"`); top-3 billed cast | AC-1.2 |

## 4. Metric definitions (AC-7.3)

| Metric | Definition |
|---|---|
| **ROI** | `(revenue − budget) / budget`, only where both are valid |
| **Profit** | `revenue − budget` (absolute) |
| **is_profitable** | `profit > 0` |
| **Budget tier** | micro `<$1M` · low `$1–10M` · mid `$10–50M` · high `$50–100M` · tentpole `≥$100M` |
| **Success** | umbrella term — always disambiguated into **revenue / profitability / reception** (PRD §8) |

## 5. Modeling method _(pending — Phase 1, FR-10)_

Target definition, leakage-free/temporal split, baseline, cross-validated metrics, feature
engineering, and interpretation (SHAP/permutation importance) documented here once built.

## 6. Model limitations _(pending — Phase 1, AC-10.7)_
