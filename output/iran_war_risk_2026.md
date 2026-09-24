# Iran War Risk and U.S. Financial Markets

An application of Rigobon and Sack (2003) to the 2026 Iran conflict

**Victor Chen** | NYU NetID: yc8027

Repository: https://github.com/victor4628/FRE7871-A3-War-Risk

## Abstract

This report applies the heteroskedasticity identification design in The Effects of War Risk on U.S. Financial Markets to Iran-war news and daily U.S. market data in 2026. Headline analysis selects high-news and nearby lower-news dates. The study reproduces the paper's two single-instrument estimates and combined-IV estimate using available financial series, and reports standard errors and weak-identification diagnostics.

Markets moved substantially around the conflict, especially oil. The two-year Treasury variance shift is too weak to assign a precise causal sensitivity to a single Iran war-risk factor. These results document the limits of this replication while preserving the observed market response.


## Executive summary

The core exercise follows the original paper's event/control heteroskedasticity design, two-year Treasury normalization, two single-instrument estimators, and combined-IV estimator. Iran-war news in 2026 replaces Iraq-war news; documented public-data proxies replace unavailable original financial series.

**Main finding:** markets moved substantially around Iran-war developments, but this study cannot determine how much was caused by one Iran war-risk factor. The two-year Treasury anchor is weak, normalized estimates vary across instruments and events, and signed-news associations do not survive multiple-comparison correction. This does not show that the war had no market effect.

| Coverage | Final study |
| --- | --- |
| Financial variables | 8 comparable outcomes plus the two-year Treasury anchor |
| Observed US sessions | 178 |
| News archive coverage | 260 calendar days, no failed dates |
| Collected / eligible / war-relevant headlines | 1,601 / 1,029 / 515 |
| Matched event / control days | 18 / 18; fewer pairs for some outcomes |

### Observed market changes are substantial

| Variable | Change since Dec 31 | Last observation |
| --- | --- | --- |
| US 2-year yield | 120.00 bp | 2026-09-17 |
| US 10-year yield | 76.00 bp | 2026-09-17 |
| S&P 500 | 11.57 % | 2026-09-17 |
| Brent spot (oil proxy) | 69.45 USD/bbl | 2026-09-15 |
| US high-yield OAS | -11.00 bp | 2026-09-17 |
| Gold ETF GLD (gold proxy) | 0.52 % | 2026-09-17 |

These are observed year-to-date changes, not effects attributable to the war. In particular, yields rose over the year while oil became more expensive; the 2003 assumption that an increase in war risk should be oriented toward a Treasury-yield fall cannot be imported automatically.

**Conflict-onset example:** on March 2, the first US session after the February 28 outbreak, Brent rose $5.92/bbl and the two-year Treasury yield rose 9 bp. Brent rose another $6.04 on March 3, a two-session gain of $11.96; the yield rose 13 bp. These are observed market moves, not causal war-effect estimates. The yield increase also makes the original paper's Treasury-fall normalization hard to interpret as an Iran-war-risk increase.


## How the two references fit together

Rigobon (2003) supplies the identification principle: changing the relative variances of otherwise orthogonal structural shocks can reveal contemporaneous relationships, provided coefficients remain stable. Multiple regimes can supply additional restrictions and tests. A proportional rise in every shock variance adds little identifying information.

Rigobon and Sack (2003) apply a narrower version to a latent war-news factor. They identify 17 news dates, compare them with nearby lower-news dates, normalize the factor to the two-year Treasury yield, and estimate effects on other financial variables. Their key restriction is that only the war factor variance changes between the two sets of dates.

### The replicated financial model

For financial changes x(t), let x(t) = b f(t) + u(t), where f is the unobserved war factor, b its stable reduced-form loadings, and u contains other common and idiosyncratic influences. With b(1) = 1 for the Treasury anchor, the identifying restriction is:

**Delta Omega = Omega(H) - Omega(L) = Delta Var(f) b b transpose.**

This implies a positive, rank-one covariance shift when H has greater war-shock variance. For outcome j, the two ratio estimators are **d1 = Delta Omega(1,j) / Delta Omega(1,1)** and **d2 = Delta Omega(j,j) / Delta Omega(1,j)**. The combined estimator uses both sign-switched instruments in 2SLS.

### NLP selects the regimes and provides a separate proxy

The news classifier identifies Iran war coverage, classifies threats, realized acts, energy exposure, and de-escalation, and measures unusually large news-flow changes. This avoids using observed market returns to choose the event dates. A separate signed-news regression estimates associations with a measurable text proxy; it does not replace the identifying assumptions of the latent-factor model.

The factor scale is arbitrary. Multiplying each relative loading by -25 bp reproduces the original table normalization. In 2026 this is a conditional Treasury-yield scenario, not a verified increase in war probability. The loadings capture total contemporaneous market responses, including spillovers; they do not separate direct effects from transmission between assets.


## The financial dataset and replication departures

The analysis uses a fixed snapshot of public daily observations, with retrieval details preserved in the source manifests. The common session calendar contains days with both Treasury and S&P observations. No missing outcome is forward-filled; an event/control pair is dropped for an outcome if either daily change is unavailable.

| Variable | Identifier | Change unit | N |
| --- | --- | --- | --- |
| US 2-year yield | DGS2 | bp | 178 |
| US 10-year yield | DGS10 | bp | 178 |
| US 10-year breakeven | T10YIE | bp | 178 |
| S&P 500 | SP500 | % | 178 |
| US BBB OAS | BAMLC0A4CBBB | bp | 178 |
| US high-yield OAS | BAMLH0A0HYM2 | bp | 178 |
| Brent spot (oil proxy) | DCOILBRENTEU | USD/bbl | 170 |
| Gold ETF GLD (gold proxy) | GLD | % | 178 |
| Broad US dollar | DTWEXBGS | % | 174 |

Yields and spreads use first differences multiplied by 100 to convert percentage points to basis points. S&P 500, GLD, and the broad dollar use 100 times log differences. Oil uses dollar changes per barrel.

The main table now follows the original paper's US-market scope. Constant-maturity Treasury yields replace estimated off-the-run par yields, ICE option-adjusted spreads replace the original credit spreads, Brent spot replaces 12-month oil futures, and GLD adjusted returns replace a dollar bullion-price change. A comparable public on-the-run Treasury liquidity-premium series was not obtained and is explicitly omitted. European, Japanese, global-equity, emerging-market, VIX, bilateral-FX, and duplicate WTI extensions are excluded from the replication tables.


## News NLP and independent benchmark

The corpus contains every dated article card retrieved from the Guardian Iran-tag archive between January 1 and September 17. URLs are deduplicated. Opinion, video, audio, gallery, and live-blog entries are excluded, as are headlines naming explicit financial-market outcomes. The primary classifier analyzes headlines; it does not claim full-story semantic or multilingual coverage.

| Label | Examples of included terms |
| --- | --- |
| Iran context | Iran, Tehran, Hormuz, Khamenei, Kharg, Natanz, IRGC |
| War relevance | War, strikes, missiles, military, nuclear, talks, ceasefire, blockade |
| Realized acts | Attacks, airstrikes, bombing, invasion, missiles, blockade |
| Threats | Warnings, nuclear, troop deployments, sanctions, escalation |
| Energy exposure | Hormuz, tankers, shipping, oil, gas, refineries, pipelines |
| De-escalation | Ceasefire, truce, peace, negotiation, deal, paused attacks |

A war-relevant headline must contain explicit Iran context. Clear metaphors are filtered. Labels overlap. Failed or rejected peace terms suppress the de-escalation flag. The score equals clip(max(0.25, acts + 0.5 threats + 0.75 energy + 0.5 failed peace) - effective peace, -1, 1). The daily news balance equals 100 times summed scores divided by eligible Iran-tag headlines. Empty news days have zero measured flow, not zero underlying risk.

Source: own archive NLP; published Iacoviello-Tong Iran AI-GPR monthly data. The published Iran index rises from 28.96 in January to 222.22 in March, about 7.67 times the January level. This corroborates the timing of the news surge, not the daily dictionary labels or a causal financial effect. September counts cover only 17 days. The eight available country-index months are not interpolated to daily observations.


## Event selection and nearby controls

A session is eligible for H if its absolute change in log(1 + war-relevant headline count) is in the upper 20% of non-macro news innovations and it has at least two relevant headlines. The cutoff is 1.051. L must have an innovation at or below the median and no more than half the H headline count. Controls are selected nearest in time without replacement, within ten US sessions and the same prewar/wartime period.

FOMC decision, CPI, and employment-report dates are excluded from both sets; a release on a closed-market date maps to the next joint session. This does not remove all other macroeconomic, tariff, earnings, or geopolitical news. Weekend and holiday news is accumulated into the next joint Treasury/S&P session. Exact publication times are unavailable; the labels are retrospective.

| Event session H | Control session L | War news H | War news L | Innovation H |
| --- | --- | --- | --- | --- |
| 2026-01-12 | 2026-01-08 | 3 | 1 | 1.39 |
| 2026-01-26 | 2026-01-23 | 2 | 0 | 1.10 |
| 2026-02-17 | 2026-02-09 | 2 | 0 | 1.10 |
| 2026-02-19 | 2026-02-10 | 2 | 1 | 1.10 |
| 2026-02-23 | 2026-02-25 | 3 | 1 | 1.39 |
| 2026-03-02 | 2026-03-05 | 37 | 10 | 2.54 |
| 2026-03-16 | 2026-03-12 | 21 | 8 | 1.99 |
| 2026-03-23 | 2026-03-19 | 16 | 6 | 1.73 |
| 2026-03-24 | 2026-03-25 | 4 | 2 | 1.22 |
| 2026-04-08 | 2026-04-02 | 14 | 6 | 1.10 |
| 2026-04-09 | 2026-04-15 | 4 | 1 | 1.10 |
| 2026-05-04 | 2026-05-01 | 5 | 1 | 1.10 |
| 2026-05-26 | 2026-05-22 | 7 | 0 | 2.08 |
| 2026-06-08 | 2026-06-04 | 6 | 2 | 1.95 |
| 2026-06-11 | 2026-06-03 | 2 | 1 | 1.10 |
| 2026-06-22 | 2026-06-18 | 8 | 2 | 1.10 |
| 2026-07-13 | 2026-07-09 | 4 | 2 | 1.61 |
| 2026-08-24 | 2026-08-21 | 5 | 0 | 1.79 |

This is the complete source-paper Table 1 analogue. A session includes all mapped news, potentially from the preceding weekend; it is not a single signed event. Sources and individual labels are in headline_scores.csv. Both escalation and peace news qualify. Main-period prewar events are sparse; an isolated prewar regression does not meet the eight-pair reporting threshold.

The March 2 event is paired with March 5 because the latter has lower measured headline innovation, yet Brent also rose $7.03 on March 5. A low-news control can still contain substantial war-related market movement during an active conflict. This weakens the clean high-versus-low war-shock-variance comparison required by the paper.


## Selected war news developments from January to March

These descriptions summarize selected developments in each mapped event session. They are an audit aid, not additional selection criteria or a signed shock measure. A session can contain escalation and de-escalation together. Weekend stories appear in the next US session.

| US session | Developments in the mapped news window | Traceability |
| --- | --- | --- |
| 2026-01-12 | Warnings about US intervention amid Iranian protests, alongside offers of talks. | [Article](https://www.theguardian.com/world/2026/jan/11/iran-arrests-protest-leaders-as-crackdown-intensifies-amid-threat-of-us-intervention) |
| 2026-01-26 | US naval deployment and Iranian warnings of retaliation if strikes occur. | [Article](https://www.theguardian.com/world/2026/jan/26/iran-prepares-possible-attack-us-navy) |
| 2026-02-17 | Nuclear negotiators report agreement on guiding principles after renewed talks. | [Article](https://www.theguardian.com/world/2026/feb/17/iran-us-nuclear-talks-open-geneva) |
| 2026-02-19 | Disputes over base access and reporting on possible US attacks on Iran. | [Article](https://www.theguardian.com/world/2026/feb/19/donald-trump-turns-against-uk-chagos-islands-plan-iran) |
| 2026-02-23 | Iran prepares a nuclear proposal as Washington considers limited strikes. | [Article](https://www.theguardian.com/world/2026/feb/21/iran-nuclear-counterproposal-us-strikes-threat) |
| 2026-03-02 | Weekend US-Israeli attacks and Iranian retaliation expand into regional conflict. | [Article](https://www.theguardian.com/world/2026/feb/28/us-israel-launch-strikes-attack-iran-what-we-know-so-far-latest) |
| 2026-03-16 | Threats against Kharg oil infrastructure and discussion of reopening Hormuz. | [Article](https://www.theguardian.com/world/2026/mar/14/us-kharg-island-oil-export-hub) |
| 2026-03-23 | Energy-infrastructure threats coincide with paused attacks and renewed diplomacy. | [Article](https://www.theguardian.com/world/2026/mar/23/israel-launches-new-strikes-on-tehran-as-trump-pauses-iran-energy-attacks) |
| 2026-03-24 | Pakistan pursues mediation while Britain proposes talks on reopening Hormuz. | [Article](https://www.theguardian.com/world/2026/mar/24/pakistan-army-chief-iran-peace-talks-trump-call) |

The source companion lists the representative article URL, original publication date inferred from its URL, mapped US session, and these research descriptions. All other articles behind each event remain in headline_scores.csv. The source link does not imply that the selected article captures every development on the date.


## Selected war news developments from April to August

These descriptions summarize selected developments in each mapped event session. They are an audit aid, not additional selection criteria or a signed shock measure. A session can contain escalation and de-escalation together. Weekend stories appear in the next US session.

| US session | Developments in the mapped news window | Traceability |
| --- | --- | --- |
| 2026-04-08 | A two-week ceasefire is announced amid disputes over shipping and regional scope. | [Article](https://www.theguardian.com/world/2026/apr/08/hegseth-press-briefing-iran-ceasefire) |
| 2026-04-09 | Disagreement over Lebanon and the scope and durability of the ceasefire. | [Article](https://www.theguardian.com/world/2026/apr/09/israel-lebanon-iran-war-ceasefire) |
| 2026-05-04 | US naval action and ship guidance plans confront the Hormuz blockade. | [Article](https://www.theguardian.com/world/2026/may/02/trump-us-navy-pirates-iran-blockade) |
| 2026-05-26 | Ceasefire proposals and prospective peace terms coexist with continuing attacks. | [Article](https://www.theguardian.com/world/2026/may/24/iran-leader-and-security-council-still-need-to-approve-peace-deal-with-us) |
| 2026-06-08 | Iran-Israel exchanges of strikes raise questions about the ceasefire. | [Article](https://www.theguardian.com/world/2026/jun/08/israel-netanyahu-airstrikes-iran-retaliation-defies-trump) |
| 2026-06-11 | Reports on strikes against water facilities and renewed uncertainty over the truce. | [Article](https://www.theguardian.com/world/2026/jun/11/strikes-water-facilities-iran-war-crime-experts) |
| 2026-06-22 | Interrupted negotiations and nuclear inspection arrangements create mixed signals. | [Article](https://www.theguardian.com/world/2026/jun/19/us-iran-talks-in-switzerland-cancelled) |
| 2026-07-13 | Renewed US strikes and blockade announcements intensify the contest over Hormuz. | [Article](https://www.theguardian.com/world/2026/jul/13/us-launches-third-night-of-strikes-on-iran-as-trump-announces-hormuz-blockade) |
| 2026-08-24 | Fresh US sanctions threats and Iranian retaliation warnings dominate coverage. | [Article](https://www.theguardian.com/world/2026/aug/23/iran-new-security-chief-trump-economic-war-enemies-mohsen-rezaei) |

The source companion lists the representative article URL, original publication date inferred from its URL, mapped US session, and these research descriptions. All other articles behind each event remain in headline_scores.csv. The source link does not imply that the selected article captures every development on the date.


## Table 2: Market Sensitivities

**Scenario:** a latent-factor movement associated with a 25 bp decline in the US two-year yield. These estimates are supplied to replicate the original calculations; weak identification prevents treating them as calibrated increases in Iran war risk. An apparently precise combined-IV standard error does not resolve weak identification.

| Outcome | Unit | Pairs | IV1 est. (SE) | IV2 est. (SE) | Both IVs est. (SE) |
| --- | --- | --- | --- | --- | --- |
| US 10-year yield | bp | 18 | -27.30* (14.41) | -22.59*** (6.09) | -21.57*** (5.96) |
| US 10-year breakeven | bp | 18 | -8.22 (7.51) | -14.00 (10.19) | -9.54 (7.17) |
| S&P 500 | % | 18 | 2.00 (2.03) | 10.01 (12.12) | 1.85 (2.02) |
| US BBB OAS | bp | 18 | 6.36 (9.60) | -0.86 (6.20) | 2.24 (3.10) |
| US high-yield OAS | bp | 18 | 9.65 (21.79) | 67.05 (164.30) | 19.06 (23.49) |
| Brent spot (oil proxy) | USD/bbl | 17 | -19.59 (16.47) | -53.02 (58.17) | -25.33 (21.73) |
| Gold ETF GLD (gold proxy) | % | 18 | 0.28 (5.69) | -9.82 (444.97) | 0.40 (4.51) |
| Broad US dollar | % | 18 | -1.32 (1.09) | -2.00 (2.75) | -1.46 (1.19) |

Heteroskedasticity-robust standard errors are in parentheses. Stars use two-sided normal-reference p values: * p < 0.10, ** p < 0.05, *** p < 0.01. IV1 uses sign(H/L) times the Treasury change; IV2 uses sign(H/L) times the outcome change; the combined estimator uses both. The regressions follow the paper's zero-mean, no-intercept formulation. With a weak first stage, conventional SEs and stars can be misleading, so the next page also reports weak-IV-robust confidence sets.

The S&P conditional response is +1.85%, and the Brent response is -$25.33/bbl under the combined instruments. Their signs differ from the 2003 Iraq findings. Because the anchor is weak and the sign of a 2026 war shock is unverified, those signs are evidence against mechanically importing the original scenario, not evidence that war reliably benefits equities or lowers oil prices.


## Uncertainty and identification diagnostics

The anchor second-moment shift is 12.67 bp squared. Its 95% circular pair-block bootstrap interval is [-5.45, 33.35]. The IV1 robust first-stage F statistic is 0.89, far below customary strength benchmarks. Zero and negative variance shifts remain plausible.

### Confidence sets preserve denominator uncertainty

| Outcome | 95% paired moment confidence set | Unit |
| --- | --- | --- |
| US 10-year yield | [-inf, -14.93] or [4.40, +inf] | bp |
| US 10-year breakeven | [-inf, 0.90] or [6.31, +inf] | bp |
| S&P 500 | [-inf, +inf] | % |
| Brent spot (oil proxy) | [-inf, +inf] | USD/bbl |
| Broad US dollar | [-inf, -0.16] or [1.74, +inf] | % |
| Gold ETF GLD (gold proxy) | [-inf, +inf] | % |

Sets invert the IV1 difference-moment test using paired contributions with HAC covariance across the ordered pairs. They retain unbounded and disconnected regions. Thus a zero restriction can sometimes be rejected without identifying a finite magnitude or unique sign. Small-sample coverage is approximate. Percentile ratio intervals are also saved, but are not reliable replacements for unbounded sets.

For seven outcomes and 17 common pairs, 12.8% of the standardized covariance-shift energy remains outside its best positive rank-one approximation. The centered block-bootstrap diagnostic has p = 0.461. The one-factor restriction is not rejected at 5%, but the test has little power with this sample; it does not verify homoskedastic other shocks, orthogonality, stable loadings, or that the factor is war risk.


## Comparison with the original Iraq war results

The original combined-instrument results were scaled to a 25 bp fall in two-year yields. Only original outcomes with interpretable 2026 counterparts are compared below. Different instrument definitions, price units, calendars, and sample composition limit numerical comparability.

| Outcome | Iraq 2003 | Iran 2026 | Comparison |
| --- | --- | --- | --- |
| US 10-year yield | -26.00 bp | -21.57 bp | Conditional only |
| US 10-year breakeven | -11.00 bp | -9.54 bp | Conditional only |
| S&P 500 | -3.76 % | 1.85 % | Conditional only |
| US BBB OAS | 5.00 bp | 2.24 bp | Conditional only |
| US high-yield OAS | 34.00 bp | 19.06 bp | Conditional only |
| Brent spot (oil proxy) | 0.77 USD/bbl futures | -25.33 USD/bbl | Proxy differs |
| Gold ETF GLD (gold proxy) | 1.30 USD gold | 0.40 % | Proxy differs |
| Broad US dollar | -0.44 % | -1.46 % | Conditional only |

### The original mechanisms need not carry over

The 2003 paper found weaker equities, wider low-grade spreads, lower Treasury yields and inflation compensation, a weaker dollar, and higher year-ahead oil futures. Gold and Treasury liquidity premiums were not significantly affected. The 2026 application includes anticipation, active conflict, shipping disruption, negotiations, and repeated escalation over a longer period.

Energy disruption could raise inflation pressure and yields while growth fears could lower them. This is an economic interpretation of competing channels, not an identified decomposition in this study. Under the covariance-only estimator the shock direction remains ambiguous, and the weak Treasury denominator magnifies that ambiguity.

Consequently, the paper's 2003 elasticities should not be used as 2026 Iran portfolio stress parameters. The replicated 2026 point estimates are diagnostic outputs pending stronger identification, not replacement calibrated stress parameters.


## Table 3: Variance Calculations

The paper's predicted shift for outcome j is d(j) squared times the anchor second-moment shift. The H share divides this by the observed H second moment. The all-session calculation divides the matched-event contribution by the sum of daily squared changes across available 2026 sessions. These are conditional algebraic calculations; causal lower-bound interpretation additionally requires valid identification and serial independence.

| Outcome | L moment | H moment | Predicted shift | H % | All % |
| --- | --- | --- | --- | --- | --- |
| US 10-year yield | 11.778 | 24.278 | 9.430 | 38.8 | 5.1 |
| US 10-year breakeven | 3.556 | 5.889 | 1.844 | 31.3 | 4.1 |
| S&P 500 | 0.423 | 0.829 | 0.070 | 8.4 | 1.0 |
| US BBB OAS | 1.222 | 1.111 | 0.101 | 9.1 | 0.7 |
| US high-yield OAS | 15.444 | 28.556 | 7.365 | 25.8 | 2.9 |
| Brent spot (oil proxy) | 20.824 | 38.324 | 10.807 | 28.2 | 5.5 |
| Gold ETF GLD (gold proxy) | 2.967 | 2.912 | 0.003 | 0.1 | 0.0 |
| Broad US dollar | 0.105 | 0.158 | 0.043 | 27.4 | 5.7 |

Moments have each outcome's daily-change unit squared. Financial outcomes have different units and cannot be compared by raw variance size. Outcome-specific missing pairs account for different samples.

**No reported share is endorsed as an identified war-risk variance bound.** Weak loadings can generate implausible shares, while some observed outcome variances actually decline on H days. A numerically admissible percentage alone does not establish a causal decomposition. The CSV preserves raw results and flags percentages outside [0,100] rather than clipping them.


## Signed news sensitivities for replication variables

This separate model regresses each daily financial change on standardized signed-news changes, attention changes, lagged financial changes, month effects, and scheduled macro-release indicators. HAC errors use five lags. One standard deviation of the news change is 40.14 news-index points; it is not a one-percentage-point change in war probability.

| Outcome | Unit | Per news SD | 95% HAC interval | FDR q | N |
| --- | --- | --- | --- | --- | --- |
| US 2-year yield | bp | -0.476 | [-1.086, 0.135] | 0.465 | 177 |
| US 10-year yield | bp | -0.333 | [-0.947, 0.281] | 0.518 | 177 |
| US 10-year breakeven | bp | -0.151 | [-0.509, 0.207] | 0.593 | 177 |
| S&P 500 | % | -0.014 | [-0.116, 0.087] | 0.782 | 177 |
| US BBB OAS | bp | 0.022 | [-0.126, 0.169] | 0.782 | 177 |
| US high-yield OAS | bp | 0.481 | [-0.059, 1.021] | 0.465 | 177 |
| Brent spot (oil proxy) | USD/bbl | 0.415 | [-0.157, 0.988] | 0.465 | 166 |
| Gold ETF GLD (gold proxy) | % | 0.125 | [-0.097, 0.348] | 0.518 | 177 |
| Broad US dollar | % | 0.015 | [-0.025, 0.054] | 0.593 | 173 |

All contemporaneous intervals include zero. The smallest Benjamini-Hochberg adjusted q value is 0.465. None of the 9 replication variables reaches q < 0.05. Point estimates suggest higher oil prices and wider high-yield spreads alongside lower Treasury yields, but the data do not establish those responses statistically.

Dictionary measurement error, single-outlet selection, post-event reporting, missing timestamps, mixed peace and conflict news, and confounding macro shocks limit interpretation. These results are associations with measured news flow, not structural causal estimates.


## Robustness and market timing

| Specification | Max pairs | 10-year bp | S&P % | Brent USD | Dollar % |
| --- | --- | --- | --- | --- | --- |
| Top 10% news innovations | 10 | -18.98 | -0.75 | -28.06 | -1.34 |
| Top 25% news innovations | 25 | -19.98 | -0.78 | -20.62 | -1.21 |
| News mapped one session later | 19 | -25.77 | 2.88 | -11.69 | -1.20 |
| Wartime only, local cutoff | 17 | -24.91 | 4.20 | -46.47 | -1.03 |
| Exclude March 2 to 6 | 17 | -21.13 | 4.65 | -43.76 | -1.27 |

Each row uses the same -25 bp Treasury normalization. Cutoff changes redefine H and matching. Outcome samples can be smaller than the maximum pair count. The next-session rule shifts news features before selecting H/L. A prewar-only estimate is suppressed because it has fewer than eight matched pairs.

The independent signed-news regressions also use next-session timing and a lead-news placebo. Their smallest corrected q values are 0.743 and 0.549, respectively. No robust predictive association emerges. A nonsignificant lead placebo cannot establish causality, particularly when the contemporaneous signal is itself weak.

FRED spot oil, Treasury, broad-dollar, and equity observations are not synchronized intraday. This timing limitation remains even after restricting the main table to the original paper's US-market scope.


## What the evidence supports

**The 2026 Iran conflict coincides with substantial news intensity and market changes, but this public-data application does not isolate a precise single war-risk factor.** The March 2-3 Brent rise documents a large market move around the outbreak. The failed identification and statistically inconclusive signed-news regressions concern this model's ability to attribute and size the effect; they do not show that war had no financial effect.

### Use the estimates as research diagnostics

The original model's Treasury normalization is weak in this application. Some conditional estimates point in different directions across instruments or event definitions. The variance shares depend on those same unstable loadings. Therefore they cannot serve as reliable portfolio stress coefficients or as an attribution of year-to-date market returns.

### Separate the most relevant channels in a stronger design

A subsequent structural extension should distinguish threat and escalation news, actual energy-supply disruptions, and diplomacy or ceasefire news. For N financial variables and K latent common shocks, Rigobon's general method requires enough independent regimes and restricted structural covariances; adding extra NLP labels does not automatically identify additional financial shocks. Three or more independent regimes can help test stable loadings, but stronger economic restrictions are still needed.

### The data that would most improve identification

A licensed corpus of full news texts with original publication timestamps would allow semantic actor, event, novelty, and direction coding, source-balanced daily denominators, and multilingual coverage. Classifier scores should be checked against a held-out human-coded sample. News windows should be aligned to market closing times and screened for overlapping macro announcements without using market returns to select events.

Intraday oil-futures curves, inflation-linked and nominal yields, credit instruments, and the original Treasury liquidity measure would reduce proxy and timing differences. Any alternative anchor must show a strong variance shift and have its shock sign established using independent news. An oil anchor could be useful for an energy-disruption factor, but would not by itself identify broader war risk.

The repository contains the data snapshot, scripts, and tables for independent examination of event labels, estimator assumptions, and uncertainty calculations.


## Sources and reproducibility

**References**  
Rigobon, Roberto (2003). "Identification through Heteroskedasticity." *The Review of Economics and Statistics* 85(4), 777-792.  
Rigobon, Roberto and Brian Sack (2003). "The Effects of War Risk on U.S. Financial Markets." NBER Working Paper No. 9609. The event-selection design and Tables 1-3 provide the basis for this application.

**News and NLP benchmark**  
Guardian dated Iran-topic archive, January 1 to September 17, 2026. [Guardian Iran archive](https://www.theguardian.com/world/iran).  
Iacoviello, Matteo and Jonathan Tong (2026). The AI-GPR Index: Measuring Geopolitical Risk using Artificial Intelligence. Published monthly Iran-country series and methodology. [Author data and paper](https://www.matteoiacoviello.com/ai_gpr.html). This benchmark is descriptive and not an Iran-specific daily regressor.

**Financial data**  
FRED daily series DGS2, DGS10, T10YIE, SP500, BAMLC0A4CBBB, BAMLH0A0HYM2, DCOILBRENTEU, and DTWEXBGS. Federal Reserve, EIA, S&P, and ICE BofA source series accessed via [FRED](https://fred.stlouisfed.org).  
Yahoo Finance daily adjusted-close history for GLD. The market sample ends September 17, 2026, with an earlier last observation for Brent. Download times and source URLs are recorded in the repository manifests.

**Macro calendars**  
[Federal Reserve FOMC calendar](https://www.federalreserve.gov/monetarypolicy/fomccalendars.htm); [BLS CPI calendar](https://www.bls.gov/schedule/news_release/cpi.htm); [BLS employment calendar](https://www.bls.gov/schedule/news_release/empsit.htm). Dates are preserved in summary.json and analyze.py.

### Reproduce and inspect

**Code, data, and report**  
[https://github.com/victor4628/FRE7871-A3-War-Risk](https://github.com/victor4628/FRE7871-A3-War-Risk)

README.md explains execution and departures. The scripts retrieve sources, score headlines, select H/L pairs, estimate all models, test algebra and units, and build this report from saved estimates. The principal tables are table2_sensitivities.csv, table3_variance.csv, and news_associations.csv. Source manifests record URLs and hashes. Bootstrap seeds are fixed; the main estimator uses 1,999 draws, and robustness tables use 399 draws.

Validation recovered known positive and negative factor loadings in simulated data, verified equality of IV1 and the covariance ratio, checked disjoint matching and macro exclusions, checked basis-point conversions and the shock scale, and confirmed complete archive coverage. Verification establishes implementation correctness, not economic identification.
