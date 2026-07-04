# Decisions Log (ADR-style)

Short, dated entries recording *why* each non-obvious choice was made. These are the
"analytics" surface for the engineering of the product (PRD §15) and the material a
reviewer probes in an interview.

---

### D1 — Data source: TMDB 5000 (OQ8 resolved) · 2026-07-05

**Decision:** Build on the **TMDB 5000 Movie Dataset** (`tmdb_5000_movies.csv` +
`tmdb_5000_credits.csv`), with an optional IMDB `title.ratings` enrichment held in
reserve for the Critics-vs-Audience view (FR-5).

**Why:** Maximises evaluator signal per unit of risk. It matches PRD §12 field-for-field,
forces exactly one meaningful join (credits ⋈ movies) as an ETL signal without join
sprawl, and is bounded (~4,800 films) so every cleaning decision is auditable.

**Rejected:** *The Movies Dataset (45k)* — its 26M-row `ratings.csv` is a scope trap that
pulls toward a recommender (rejected by the PRD, N3/Appendix C). *An upfront manual
TMDB↔IMDB merge* — fragile id reconciliation front-loaded into P0.

**Known cost:** TMDB gives only an audience score (`vote_average`), no critic score. FR-5
needs the IMDB enrichment (join on `imdb_id`) — deferred, not designed away.

---

### D2 — budget == 0 and revenue == 0 are treated as *missing*, not real · 2026-07-05

**Decision:** Rows with `budget == 0` or `revenue == 0` are flagged (`financials_valid = False`)
and **excluded from ROI/profit**, never silently kept (AC-1.3).

**Why:** In TMDB a financial field of 0 overwhelmingly means "not reported", not "$0".
Keeping them would inject enormous fake losses/gains and corrupt every profitability metric.

**Implication:** The ROI-analysis sample is smaller than the full corpus and is
**non-randomly missing** (indie/foreign films are likelier to lack financials) — a bias we
disclose on the Methodology page rather than hide.

---

### D3 — Non-zero but implausibly small financials are flagged too · 2026-07-05

**Decision:** A non-zero budget or revenue below **$1,000** (`MIN_PLAUSIBLE_FINANCIAL`) is
treated as a data-entry error and excluded from ROI.

**Why:** A "$12 budget" produces absurd ROI outliers that would dominate medians and plots.
Zero-handling alone doesn't catch these.

---

### D4 — Median over mean for ROI · 2026-07-05

**Decision:** Headline profitability uses **median** ROI (and distributions), not mean.

**Why:** ROI is extremely heavy-tailed — a single microbudget breakout (huge ROI) drags the
mean into meaninglessness. Median + box/violin distributions (AC-3.3) are the honest summary.

---

### D5 — Reproduce the join ourselves; don't rely on a pre-merged file · 2026-07-05

**Decision:** The ETL joins `credits` onto `movies` on `id` itself (AC-1.2, §12.1).

**Why:** Demonstrating the join is an explicit evaluator signal, and it keeps provenance of
every column clear.

---

### D6 — Multi-genre attribution: films count toward *each* genre · 2026-07-05

**Decision:** A film with N genres is attributed to all N; we **never sum** a metric across
genres (that double-counts), and we surface this caveat in the Profitability view (AC-3.4).

**Why:** Summing gross across genres is the classic misleading movie-data metric
(Appendix C). Medians/shares per genre are safe; sums are not.

---

_Add new entries above this line as decisions are made._
