# Data Dictionary — `data/processed/movies_clean.parquet`

The clean, analytical dataset emitted by `pipeline/etl.py`. One row per film.

| Column | Type | Role | Notes |
|---|---|---|---|
| `id` | int | key | TMDB movie id; stable, unique after dedup |
| `title` | string | identity | Whitespace-normalised; titles may collide → disambiguate by `id` |
| `original_title` | string | identity | As released in original language |
| `original_language` | string | provenance | ISO code; drives language-skew caveat |
| `budget` | float | financial | Nominal USD; `0` → treated as missing |
| `revenue` | float | financial | Nominal USD; `0` → treated as missing |
| `profit` | float | derived | `revenue − budget`; NaN where financials invalid |
| `roi` | float | derived | `(revenue − budget) / budget`; NaN where financials invalid |
| `is_profitable` | boolean | derived | `profit > 0`; NA where financials invalid |
| `financials_valid` | bool | flag | True iff budget & revenue are valid and plausible |
| `budget_valid` | bool | flag | `budget > 0` |
| `revenue_valid` | bool | flag | `revenue > 0` |
| `budget_tier` | string | derived | micro / low / mid / high / tentpole; None if budget missing |
| `vote_average` | float | reception | TMDB **audience** score (0–10); no critic score available |
| `vote_count` | int | reception | Reliability filter for noisy low-vote films |
| `popularity` | float | reception | TMDB popularity; **post-release → excluded from pre-release model** |
| `runtime` | float | content | Minutes |
| `genres` | list[str] | content | Parsed from JSON; a film may have several |
| `keywords` | list[str] | content | Parsed from JSON; optional NLP |
| `production_countries` | list[str] | provenance | Parsed from JSON |
| `production_companies` | list[str] | content | Parsed from JSON |
| `director` | string | talent | First crew member with `job == "Director"` |
| `cast_top` | list[str] | talent | Up to 3 top-billed actors |
| `release_date` | datetime | content | Parsed; NaT if unparseable |
| `release_year` | float | derived | From `release_date` |
| `release_month` | float | derived | From `release_date` (seasonality) |

> ⚠ **Leakage note (for FR-10):** `vote_average`, `vote_count`, and `popularity` are
> **post-release** signals. They must **not** be used as features to predict a pre-release
> target (AC-10.2). They are fine as descriptive/reception fields in the app.
