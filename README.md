# Iran war risk in 2026

Empirical application of Roberto Rigobon's **Identification through Heteroskedasticity** (2003) and Rigobon and Sack's **The Effects of War Risk on U.S. Financial Markets** (2003), with a transparent news NLP extension. Market observations end on **September 17, 2026**. This is a retrospective research study.

The final application covers **9 original-paper-scope financial variables (including the Treasury anchor), 178 sessions, 1,029 eligible headlines, 515 war-relevant headlines, and 18 matched event/control pairs**. It is a direct Iran-2026 analogue of the Rigobon-Sack design: the war setting and news classification change, while the core US-market variable scope, event/control variance comparison, Treasury normalization, two IV estimators, and combined-instrument estimator follow the paper. The Treasury anchor is weak (IV1 robust first-stage F **0.886**; its second-moment shift has a block-bootstrap interval spanning zero). No signed-news association survives false-discovery correction. The conditional replication estimates are **exploratory**, not reliable causal Iran war-risk sensitivities. This analysis was not preregistered.

**Interpretation:** The inability of this specification to isolate a precise causal effect does not mean the war had no market effect. On March 2, the first US session after the February 28 outbreak, Brent spot rose **$5.92/bbl** and the US two-year Treasury yield rose **9 bp**. Brent rose another **$6.04/bbl** on March 3. These are observed, coincident movements, not estimates of how much of the change the war caused. The March 5 matched control also saw a **$7.03/bbl** Brent increase despite lower measured news innovation, illustrating the difficulty of finding genuinely low-war-risk days during active conflict.

## Deliverables

- `output/pdf/iran_war_risk_2026.pdf`: methodology, findings, replication tables, diagnostics, and event/control appendix.
- `output/analysis/table2_sensitivities.csv`: the two covariance-ratio estimates and combined-instrument estimate, normalized to a 25 bp fall in the US two-year yield, with heteroskedasticity-robust standard errors and p values for all three estimates plus weak-IV diagnostics.
- `output/analysis/table3_variance.csv`: source-paper variance calculations. Raw shares are conditional calculations, not validated causal bounds.
- `output/analysis/news_associations.csv`: separate contemporaneous, next-session, and lead-placebo regressions, with HAC uncertainty and false-discovery correction.
- `output/analysis/event_control_pairs.csv`: market-independent selection and nearby matching.
- `output/analysis/event_sources.csv`: descriptions of selected developments and representative article links.
- `output/analysis/headline_scores.csv` and `news_daily.csv`: auditable NLP labels and news measures.
- `output/analysis/robustness.csv`, `rank_diagnostic.json`, and `validation.json`: sensitivity checks and verification.

## Reproduce

Use Python 3.12 or a compatible version, install `requirements.txt`, and run from this directory:

```text
python scripts/download_data.py
python scripts/download_etfs.py
python scripts/download_news.py
python scripts/analyze.py
python scripts/validate.py
python scripts/build_report.py
```

Downloaded data are cached in `data/raw`. News collection proceeds serially with a pause between requests; successful archive pages are preserved. If rate limits prevent complete collection, wait and rerun the downloader; **do not interpret failed requests as zero coverage**. The analyzer excludes incomplete news sessions and differences crossing missing sessions; the validation gate requires a complete archive for the delivered study. GDELT was tested but not used because its endpoint returned HTTP 429.

The reproduction ZIP includes the extracted article input, downloaded financial/NLP data, scripts, and outputs; it omits bulky archived HTML and installed libraries. To reproduce the delivered vintage, install requirements and run **analyze, validate, build_report** against the included cache without rerunning the downloaders. A later fresh download can contain revised sources and headline edits.

The desktop execution used bundled Python and workspace-local analysis libraries under `tmp/pythonpackages`. Scripts also run with normally installed packages. Random seeds and bootstrap replication counts are fixed in the code.

## Design and interpretation

The corpus is the public **Guardian Iran-tag archive**, January 1 to September 17, 2026. The extraction keeps dated article cards, deduplicates canonical URLs, and discards cards with another publication date. The primary analysis uses **headlines**, not full article bodies. Opinion, video, audio, gallery, live-blog entries, and headlines containing explicit financial-market outcomes are excluded. Dictionary NLP classifies war relevance, realized acts, threats, energy exposure, and de-escalation. Categories overlap; a failed-peace rule suppresses misleading positive peace labels. This is a rule-based proxy without externally measured classifier accuracy.

War relevance requires an explicit Iran, Tehran, Hormuz, Khamenei, Kharg, Natanz, or IRGC context. Clear metaphors such as "ticking bomb" and "social media wars" are filtered. A signed article score is `clip(max(0.25, acts + 0.5*threats + 0.75*energy + 0.5*failed_peace) - effective_peace, -1, 1)` for relevant articles, and zero otherwise. The daily news balance is 100 times the sum of scores divided by the eligible Iran-tag article count (a zero denominator gives a zero news-flow measure). A zero value means no net measured news flow, not an absence of underlying war risk.

News on weekends and US market holidays is mapped to the next observed joint Treasury/S&P session. Scheduled macro releases on a closed-market date are likewise mapped to the next joint session (for example, the April 3 employment release maps to April 6). Exact publication times are unavailable, so same-day estimates are retrospective; a next-session specification checks timing sensitivity. These results cannot establish an intraday tradable signal.

High-news days are the upper 20% of absolute changes in log(1 + relevant headline count), after excluding FOMC decision, CPI, and employment-report dates, and must contain at least two relevant headlines. Each event is matched without replacement to the nearest eligible low-news session at or below the median innovation and with at most half the event's relevant headline count, within ten US sessions and within the same prewar/wartime period. The March 2 boundary is the first US session after the February 28 outbreak. Selection does not inspect market returns. Alternative cutoffs and period splits are supplied. Obvious relevance errors and event days with no war headlines were corrected before the final specification; those corrections were not chosen to maximize significance.

The main market model is restricted to the original paper's scope: the US two-year Treasury anchor, US ten-year Treasury yield, ten-year breakeven inflation, S&P 500, BBB and high-yield credit spreads, oil, gold, and the broad US dollar. European, Japanese, global-equity, emerging-market, VIX, bilateral-FX, and duplicate oil extensions are excluded. Yields and spreads use changes in **basis points**, S&P 500/GLD/dollar returns use **100 times log differences**, and oil uses changes in **dollars per barrel**. Missing observations are not filled. Source-paper second moments assume zero means; regime-centered covariance estimates are provided as a check. Combined-instrument 2SLS uses both sign-switched financial changes. Its algebra follows the source paper, but causal validity still requires that only the war shock's variance changes and that loadings are stable and other shocks orthogonal.

Block bootstrap ratio intervals are descriptive when the Treasury anchor is weak. The paired, HAC difference-moment confidence set preserves unbounded or disjoint intervals instead of hiding denominator uncertainty. A standardized seven-variable positive-semidefinite rank-one residual test provides an approximate bootstrap diagnostic of the one-factor restriction. Failure to reject does not verify orthogonality or identify the shock as war risk.

The separate NLP association model controls for lagged financial changes, news attention changes, month effects, and scheduled macro-report days; it uses Newey-West/HAC errors with five lags. A one-standard-deviation signed-news change is a sample-specific proxy change, **not a probability-of-war change**. News reporting can react to events and markets. Do not describe these coefficients as causal effects or compare them numerically with the 25 bp normalized IV estimates.

## Sources and departures from an exact replication

The supplied papers are retained unchanged at the repository root. Raw download manifests include source URLs and, for the main series and news archives, content hashes.

- FRED series pages: `https://fred.stlouisfed.org/series/<SERIES_ID>`; main-table providers include the Federal Reserve, EIA, S&P Dow Jones, and ICE BofA.
- Public ETF history: Yahoo Finance daily chart response for GLD. Adjusted closes are used. GLD is an ETF return proxy for gold, not a dollar bullion-price response.
- NLP benchmark: Iacoviello and Tong (2026), `https://www.matteoiacoviello.com/ai_gpr.html`. The public Iran-country series is monthly and is used for descriptive validation only, without interpolating it into daily observations or pretending eight months provide a daily shock series.
- Macro calendars: `https://www.federalreserve.gov/monetarypolicy/fomccalendars.htm`, `https://www.bls.gov/schedule/news_release/cpi.htm`, and `https://www.bls.gov/schedule/news_release/empsit.htm`.

Treasury constant-maturity yields replace estimated off-the-run par yields; ICE option-adjusted spreads replace the original credit spreads; Brent spot replaces year-ahead oil futures. No comparable public 2026 on-the-run/off-the-run liquidity-premium series was obtained, so that original outcome is explicitly omitted. The broad dollar definition and gold measurement also differ. The 2026 sample includes both anticipation and realized war, whereas the original main sample focused on the buildup to the Iraq war.

Raw newspaper and financial data retain their source owners' rights, including ICE and Yahoo/provider restrictions. The local cache is for this user's research; this repository does not grant republication rights to source data. Estimates and uncertainty must be read with the report's identification findings.
