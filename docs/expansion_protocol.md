# EARS Dictionary v2 Expansion Protocol — v2.1

**Version:** 2.1 (replaces v2.0)
**Frozen:** 2026-04-29
**Driver of revision:** independent agent review of v2.0 surfaced two fatal flaws (construct-definition leakage into prompts; 8-word "calibration" set was mostly memorization) plus several non-fatal issues. v2.1 rewrites accordingly.

## Method, in one paragraph

Take the 297 Loughran-McDonald "Uncertainty" words and lemmatize to ~200 unique lemmas. Have two human researchers (Daniel + one collaborator) hand-code a stratified sample of 30 lemmas, blind to each other and blind to any LLM run. This human gold set is the reliability anchor. For each lemma, sample real usage contexts (5 for typical lemmas; 25 for the high-frequency polysemous ones in the top decile by corpus frequency). Submit each lemma + its contexts + a leakage-free construct definition to a 5-prompt LLM ensemble. Aggregate to a per-lemma label. Gate the entire procedure on the LLM ensemble matching the human gold set at Cohen's kappa >= .60. If the gate passes, apply the LLM tags to the remaining lemmas and validate on held-out transcripts using a non-circular outcome.

## What changed from v2.0

- **Definition leakage (FATAL):** v2.0 fed the construct definitions verbatim into the prompts, including example phrases that contained LM 297 words (`volatility`, `probability`, `confident`, `model`, `suggests`). Several of those words then appeared in the calibration set, where the prompt was effectively telling the rater the answer. **v2.1 uses a leakage-free version of the definitions in the prompts.** All word-level examples are replaced with abstract conceptual examples that do not appear in LM 297.
- **Calibration (FATAL):** v2.0 treated the 8 v1-EARS ∩ LM-297 overlap words as a calibration set. Of those 8, five were in the construct definition fed to the rater, so passing was mostly memorization. **v2.1 replaces this with a hand-coded human gold set of 30 LM lemmas.** Coded by Daniel + one collaborator, blind to each other, before any LLM call. Reported metric: Cohen's kappa between LLM ensemble and human consensus.
- **Polysemy (significant):** v2.0 sampled 5 contexts per word, which is too few for high-frequency polysemous items like `model`, `expect`, `sure`, `likely`. **v2.1 stratifies sampling: 5 contexts for typical-frequency lemmas, 25 contexts for top-decile-frequency lemmas. For high-frequency lemmas, return a sense distribution (% epistemic / % aleatory / % neither across contexts) rather than a single label.**
- **Inflection (significant):** v2.0 classified all 297 forms independently, including 6-way redundancies (anticipate / anticipated / anticipates / ...). **v2.1 lemmatizes first.** Classify ~200 lemmas; expand to inflections post-hoc.
- **Predictive circularity (significant):** v2.0 required the v2 dictionary to reproduce the surprise → E/A pattern that was discovered using v1, which is gating "is v2 like v1?" rather than validating v2. **v2.1 demotes that test to a descriptive comparison and adds a non-circular predictive criterion: predicting analyst forecast dispersion (an established aleatory proxy) and predicting analyst forecast revision speed (an epistemic proxy) — outcomes that were not used in building v1.**
- **Reproducibility (moderate):** v2.0 didn't pin model version, didn't cache responses, used temperature 0.7 N=1 (worst of both worlds). **v2.1 pins the exact Claude snapshot, caches all raw API responses, and uses temperature 0 N=1 deterministic per prompt** (so any rater disagreement is purely a prompt effect).
- **Per-category metrics (moderate):** v2.0 reported only Krippendorff's alpha on a 4-category nominal scale. With imbalanced marginals this can be misleading. **v2.1 also reports per-category Cohen's kappa, the full confusion matrix, and majority-class baseline.**
- **Ensemble interpretation (moderate):** v2.1 explicitly acknowledges that the 5 prompts are five draws from one model, not five independent annotators. The within-Claude alpha is reported as a *prompt-stability* statistic. The reliability statistic that gates the protocol is kappa-vs-human-gold-set. If GPT-4 / Gemini / Llama API access becomes available later, a cross-model alpha will be added as a robustness check (out of scope for v2.1).

## Binding constraints

- The 297 LM words are the input; no expansion beyond LM.
- Construct definitions in `docs/construct_definitions.md` are the operational basis for human and LLM coding alike, but the **prompt-fed version** for LLM raters is the leakage-free `docs/construct_definitions_prompt.md` (see Step 2 below).
- v1 EARS dictionary remains frozen as construct anchor; reported alongside.
- Two human raters (Daniel + 1 collaborator) hand-code the gold set. This is the only place humans enter the pipeline.
- All thresholds are written into this document before the gated computations run.
- Every rater vote, every accept/reject decision, every dropped lemma — logged in `outputs/`.

## Inputs

- **Wordlist:** `outputs/loughran_mcdonald_uncertainty_297.csv`
- **Construct definitions (full, for human reference):** `docs/construct_definitions.md` (frozen 2026-04-23)
- **Construct definitions (leakage-free, for LLM prompts):** `docs/construct_definitions_prompt.md` (frozen at execution time; see Step 2)
- **Transcript corpus:** `processed_data/stripped_corpus.txt.gz` (16,385 transcripts, P2+P3, HTML-stripped)
- **v1 EARS dictionary:** `outputs/dictionary_v1.txt` (used for descriptive comparison only)

---

## Step 0 — Lemmatize LM 297 (one-time, deterministic)

Use `nltk.WordNetLemmatizer` (or equivalent) to reduce the 297 inflected forms to their lemmas. Expected output: ~200 unique lemmas. Save as `outputs/lm297_lemmas.csv` with columns: `lemma`, `inflected_forms` (semicolon-separated), `corpus_frequency` (counted in the existing `processed_data/stripped_corpus.txt.gz`).

Stratification: lemmas are tagged as `top_decile_freq` if their corpus frequency is in the top 10% of the lemma list, else `typical_freq`.

## Step 1 — Sample corpus contexts (one-time, deterministic)

For each lemma:
- If `typical_freq`: sample 5 random KWIC windows from the corpus across all inflected forms of the lemma, target word ± 15 tokens, sentence-bounded where possible.
- If `top_decile_freq`: sample 25 random KWIC windows.

Save to `processed_data/kwic_lm_lemmas.json`. Random seed fixed for reproducibility. If a lemma's total corpus frequency is below the requested sample size, take all available contexts and note the count.

## Step 2 — Prepare leakage-free construct definitions

Author `docs/construct_definitions_prompt.md` containing:
- The plain-English definitions of epistemic and aleatory uncertainty (no examples that contain LM 297 vocabulary)
- Permitted abstract examples: a die roll for aleatory, a forecast based on private analysis for epistemic, etc., constructed to use vocabulary outside LM 297
- The 4-category classification rule (EPISTEMIC / ALEATORY / AMBIGUOUS / NEITHER)
- No example word lists. No EARS examples. No LM 297 vocabulary anywhere in the file.

Verify by grep: `grep -if outputs/loughran_mcdonald_uncertainty_297.csv docs/construct_definitions_prompt.md` should return zero matches.

This file is what the LLM raters and human gold-set coders both see as their classification rubric.

## Step 3 — Hand-code human gold set (HARD GATE)

Sample 30 lemmas via stratified random sampling from `outputs/lm297_lemmas.csv`:
- 10 from the top-decile-frequency lemmas
- 20 from the typical-frequency lemmas

Daniel and one collaborator each independently classify each of the 30 lemmas as EPISTEMIC / ALEATORY / AMBIGUOUS / NEITHER, using:
- The leakage-free definition file from Step 2
- The same 5-or-25 KWIC contexts that the LLM will see in Step 4

Both coders are blind to each other's labels and blind to any LLM output during coding.

After coding:
- Compute Cohen's kappa between the two human coders. **Pre-committed gate: kappa_humans >= 0.60.** If lower, the construct distinction is not coding-reliable for humans on this domain, full stop. Halt and reconsider construct or sampling.
- Resolve disagreements via discussion to produce a single human gold label per lemma. (Document the resolutions.)

Save to `outputs/gold_set_30.csv`.

## Step 4 — LLM ensemble classification

For each of the ~200 lemmas (gold-set lemmas included; their LLM labels are the test against the human consensus) and each of 5 prompt variants, submit a single Claude call:

- Prompt content: leakage-free definitions from Step 2; the 5 or 25 KWIC contexts from Step 1; the rating task
- Response format: typical lemmas → single label (EPISTEMIC / ALEATORY / AMBIGUOUS / NEITHER); top-decile lemmas → sense distribution (% in each of the 4 categories across the 25 contexts)

Five prompt variants:
- **A — Strict zero-shot:** definitions + contexts + classify
- **B — Chain-of-thought:** A + "Think step by step before answering. Final classification on the last line."
- **C — Expert frame:** "You are a behavioral economist. [rest same as A]"
- **D — Conservative:** A + "Default to AMBIGUOUS unless the lemma unambiguously signals one construct"
- **E — Phrase-context:** A + one example showing the lemma in a longer phrase

**Settings:** temperature 0, N=1 per prompt. Pin model snapshot (claude-opus-4-7-[date], whichever is current at execution). Cache all raw API responses to `processed_data/llm_raw_responses/` (gitignored if large; OSF-synced).

Total: 5 prompts × ~200 lemmas = ~1,000 LLM calls (~20 min API time).

For top-decile lemmas, the ensemble produces a sense distribution rather than a label; the modal sense is the lemma's tag, and the within-lemma sense disagreement is reported as polysemy intensity.

## Step 5 — Aggregate and apply per-lemma acceptance rules (pre-committed)

For each lemma, aggregate the 5 prompts' labels:
- **ACCEPT as EPISTEMIC** if >= 4 of 5 raters say EPISTEMIC
- **ACCEPT as ALEATORY** if >= 4 of 5 raters say ALEATORY
- **AMBIGUOUS** if no construct gets >= 4 votes, OR >= 3 raters say AMBIGUOUS
- **REJECT (NEITHER)** if >= 3 raters say NEITHER

Compute and report:
- Krippendorff's alpha across the 5 prompt variants. Reported as a *prompt-stability* statistic (NOT inter-rater reliability).
- Per-category Cohen's kappa (E vs not-E; A vs not-A; etc.) with majority-class baseline.
- Full confusion matrix across the 5 prompt variants.

## Step 6 — Calibration against the human gold set (HARD GATE)

For the 30 gold-set lemmas, compare the LLM-ensemble final label to the human consensus label.
- Compute Cohen's kappa between LLM-ensemble and human-consensus.
- **Pre-committed gate: kappa_LLM_vs_human >= 0.60.** If kappa is below 0.60, the LLM ensemble is not adequately tracking the human construct; halt and revise prompts or definitions before proceeding.
- Report per-category breakdown (which categories disagree most).

If the gate passes, expand the LLM-tagged lemmas back to inflected forms (each inflection inherits its lemma's tag) to produce the v2 inflected dictionary.

## Step 7 — Held-out validation (descriptive + non-circular tests)

Split transcripts 70/30 by firm (`IDPERMNO`), stratified by `surprise` group.

**7A — Convergent validity (descriptive).** Per-document Pearson r between v1 EARS scores and v2 LM-tagged scores on held-out 30%. Report; no pass/fail threshold (these are different constructs by design).

**7B — Descriptive comparison to original surprise → E/A pattern.** Re-run surprise → E/A regressions with v2 counts. Report. Not a gate (would be circular: the pattern was discovered with v1, requiring v2 to reproduce it just gates v2 → v1 similarity).

**7C — Non-circular predictive criterion (HARD GATE).** Apply v2 epistemic and aleatory counts to predict, on the held-out 30%:
- **Analyst forecast dispersion** (cross-analyst SD of EPS forecasts in the same quarter): expected to correlate POSITIVELY with v2 aleatory counts (more aleatory language = more inherent randomness in the firm's outlook = more analyst dispersion)
- **Analyst forecast revision speed** (time between consecutive forecast revisions): expected to correlate NEGATIVELY with v2 epistemic counts (more epistemic language = more new information being released = faster revisions)

Required: both predictions show effects in the predicted direction with p < .05 in the held-out sample. These outcomes were not used in v1's construction; they're true out-of-sample tests.

**7D — Top-k influence curve.** Report the fraction of words that must be dropped before the surprise → E/A signs flip. Flag if elbow is below k=5.

**7E — Concentration via effective number of contributors.** Compute Hill number (e.g., q=2 or "inverse Simpson") for the per-category word-count distribution. Report; no threshold.

## Step 8 — Deliverables

- `outputs/lm297_lemmas.csv` — lemmatization map
- `outputs/gold_set_30.csv` — human gold set with both coders' labels and resolved consensus
- `outputs/dictionary_v2.txt` — inflected v2 dictionary, each form tagged
- `outputs/dictionary_v2_lemmas.csv` — per-lemma vote table, sense distributions for top-decile lemmas
- `outputs/dictionary_v2_rejected.csv` — lemmas tagged NEITHER, with rationale
- `outputs/dictionary_v2_calibration.csv` — gold-set comparison
- `outputs/validation_report.md` — kappa_humans, kappa_LLM_vs_human, alpha_within_Claude, all confusion matrices, all Step 7 results
- `processed_data/kwic_lm_lemmas.json` — sampled corpus contexts (gitignored if large; OSF-synced)
- `processed_data/llm_raw_responses/` — cached raw API responses for full reproducibility
- `docs/construct_definitions_prompt.md` — leakage-free definitions used in LLM prompts
- `docs/expansion_protocol.md` — this document (v2.1)

## Reporting language (paper / OSF boilerplate)

> "We tagged the 297 words in the Loughran & McDonald (2011) 'Uncertainty' word list as primarily epistemic, primarily aleatory, ambiguous, or neither, using a 5-prompt LLM ensemble grounded in real usage contexts from the earnings-call corpus. The 297 inflected words were lemmatized to [N] lemmas before classification. The construct definitions used in prompts were authored to be leakage-free, containing no LM 297 vocabulary. Reliability was anchored against a hand-coded human gold set of 30 stratified lemmas (Daniel Walters and [collaborator], blind to each other and to any LLM output), with kappa_humans = [X]. The LLM ensemble's labels were validated against the human consensus, kappa_LLM_vs_human = [X], pre-committed gate >= 0.60. The resulting v2 dictionary was held-out validated on 30% of transcripts (split by firm, stratified by surprise group): predicting analyst forecast dispersion (aleatory proxy) and revision speed (epistemic proxy), both outcomes that were not used in v1's construction (Ulkumen, Fox & Malle 2016). Both v1 and v2 results are reported throughout."

## What this protocol does NOT do

- **No five-method candidate generation.** LM 297 is the input; we do not search for words beyond it.
- **No FinBERT / embedding-based classifier.** Considered and cut.
- **No cross-model LLM ensemble (out of scope).** All 5 prompts are to the same Claude snapshot. Cross-model robustness is a v2.2 deferral.
- **No LLM-only reliability claim.** Reliability is anchored against the human gold set; the LLM ensemble's internal alpha is a prompt-stability descriptor, not a reliability metric.
- **No new construct definitions.** The Fox / Ulkumen / Tannenbaum framework is binding; only its operational instantiation in prompts was rewritten to remove leakage.
- **No within-LM word reduction by curation.** Lemmas that the ensemble + gold set agree are NEITHER are dropped through the formal gate, not by hand.

## What not to do

- Do not iterate after seeing held-out outcomes in Step 7.
- Do not silently change thresholds after seeing kappa.
- Do not skip the rejection log.
- Do not run the LLM ensemble before the human gold set is coded and frozen.
- Do not show the human coders the LLM output.

## Justification for design choices (citations)

| Choice | Justification | Cite |
|---|---|---|
| Human gold set as reliability anchor | Standard in LLM-as-annotator literature; Gilardi-style validation | Gilardi et al. 2023 PNAS; Sci Reports 2025 |
| LLM ensemble (5 prompts) for the bulk classification | Stabilizes against single-prompt artifacts; cheap | Zhang et al. 2025 (arXiv 2511.15714) |
| Leakage-free prompt definitions | Standard prompt-engineering hygiene; absence is a clear methodological failure | General LLM evaluation practice |
| Lemmatization before classification | Avoids inflating effective N; standard NLP practice | Standard |
| Stratified KWIC sampling (5 vs 25 by frequency) | Polysemy is concentrated in high-frequency lexemes; recent WSD literature uses 20+ contexts | arXiv 2503.08662 |
| Temperature 0 deterministic | Separates prompt effect from sampling variance | Standard reproducibility practice |
| Model version pin + raw response cache | Reproducibility against model drift | EMNLP 2024 LLM-annotation guidelines |
| Cohen's kappa per category + confusion matrix | Robust to imbalanced marginals where alpha alone is misleading | Psychometric practice |
| Non-circular outcome (analyst dispersion / revision speed) | Avoids using v1's discovery as v2's validation gate | Out-of-sample text-as-data practice |

## Version history

- **v1.0 (2026-04-23):** Five-method candidate generation + 5-rater LLM ensemble + held-out validation, starting from 30 v1 EARS seeds. Step 2 was executed (159 surviving candidates). Steps 3-6 paused.
- **v2.0 (2026-04-29 morning):** Replaced v1.0. Dropped candidate generation; took LM 297 directly. Used 8 v1-EARS-overlap words as calibration. Used construct definitions verbatim in prompts.
- **v2.1 (2026-04-29 evening):** Replaces v2.0. Driven by independent agent review of v2.0. Adds: leakage-free prompt definitions, human-coded 30-lemma gold set as reliability anchor, lemmatization, stratified KWIC sampling for polysemous high-frequency lemmas, non-circular predictive validation criterion, model version pinning, cached raw responses, per-category kappa + confusion matrices. Removes: 8-word "calibration" set (mostly leakage), surprise → E/A pattern as a pre-committed gate (circular).
