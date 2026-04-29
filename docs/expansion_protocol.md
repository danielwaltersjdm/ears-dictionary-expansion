# EARS Dictionary v2 Expansion Protocol — v2.0

**Version:** 2.0 (replaces v1.0)
**Frozen:** 2026-04-29
**Scope shift in v2.0:** No candidate generation. The 297 Loughran-McDonald (2011) "Uncertainty" words are taken as the candidate pool directly. The protocol is now purely a **classification + validation** procedure: tag each of the 297 LM words as Epistemic / Aleatory / Ambiguous / Neither, and verify the tagged dictionary preserves the surprise → E/A pattern.

## Method, in one paragraph

Take each of the 297 Loughran-McDonald "Uncertainty" words. For each, sample 5 real usage contexts (KWIC windows) from the earnings-call corpus. Submit the word, the construct definitions, and the contexts to Claude under five different prompt framings. Aggregate the five labels via majority vote. Report inter-rater agreement (Krippendorff's alpha). Verify the method works by checking that the 8 words appearing in BOTH LM 297 AND v1 EARS get classified consistently with their v1 tags. Validate the resulting dictionary on held-out transcripts.

## Binding constraints

- The 297 LM words are the input; no expansion, no candidate generation.
- The construct definitions in `docs/construct_definitions.md` are the acceptance gate. Frozen.
- v1 EARS dictionary remains frozen as construct anchor; reported alongside.
- No human raters; LLM-only by design.
- All thresholds are written into this document before the gated computations run.
- Every rater vote, every accept/reject decision, every dropped word with reason — logged in `outputs/`.

## Inputs

- **Wordlist:** `outputs/loughran_mcdonald_uncertainty_297.csv` (297 unigrams, lowercased)
- **Construct definitions:** `docs/construct_definitions.md` (frozen 2026-04-23)
- **Transcript corpus:** `processed_data/stripped_corpus.txt.gz` (16,385 transcripts, P2+P3, HTML-stripped)
- **v1 EARS dictionary:** `outputs/dictionary_v1.txt` (30 words, used for calibration only)

---

## Step 1 — Sample corpus contexts (one-time, deterministic)

For each of the 297 LM words, sample 5 random KWIC windows from the corpus. Window = target word ± 15 tokens, sentence-bounded where possible. Save to `processed_data/kwic_lm297.json`. Total: 1,485 contexts. Random seed fixed for reproducibility.

If a word appears fewer than 5 times in the corpus, take all available contexts and note the count in the output JSON.

## Step 2 — LLM ensemble classification

For each word × each of 5 prompt variants, submit a single Claude call:

- Prompt includes: construct definitions (verbatim from `docs/construct_definitions.md`), the 5 KWIC contexts for this word, and the rating task
- Response: one of EPISTEMIC / ALEATORY / AMBIGUOUS / NEITHER

Five prompt variants:

- **A — Strict zero-shot:** Definitions + contexts + classify, single-word answer. Default temperature.
- **B — Chain-of-thought:** A, prefixed with "Think step by step before answering. Then return your final classification on the last line."
- **C — Expert frame:** "You are a behavioral economist studying variants of uncertainty. [rest same as A]"
- **D — Conservative:** A, plus "Default to AMBIGUOUS unless the word unambiguously signals one construct."
- **E — Phrase-context-aware:** A, but include one example showing the word in a longer phrase (e.g., "fairly sure" rather than just "sure").

Each at temperature 0.7, N=1 draw. Total: **1,485 LLM calls** (~30 min API time).

## Step 3 — Aggregate and apply acceptance rules (pre-committed)

For each word, aggregate the 5 labels:

- **ACCEPT as EPISTEMIC** if >= 4 of 5 raters say EPISTEMIC
- **ACCEPT as ALEATORY** if >= 4 of 5 raters say ALEATORY
- **AMBIGUOUS** if no single construct gets >= 4 votes, OR if >= 3 raters say AMBIGUOUS
- **REJECT (NEITHER)** if >= 3 raters say NEITHER

Compute Krippendorff's alpha across the 5 raters on the full 297. **Pre-committed gate: alpha >= .70 to proceed.** If alpha < .70, halt and refine prompts/definitions before continuing. If alpha < .60, halt entirely and reconsider the protocol.

## Step 4 — Calibration + validation (pre-committed thresholds)

**4A — Calibration via v1 EARS overlap.** The 8 words in v1 EARS ∩ LM 297 (`presume`, `suggests`, `likelihood`, `probability`, `variance`, `volatility`, `fluctuation`, `random`) carry known v1 tags. Apply the method's classifications. **Required: >= 7 of 8 correct.** If fewer, the method has a systematic bias — halt before trusting on novel words.

**4B — Convergent validity.** On the held-out 30% of transcripts (split by firm via IDPERMNO, stratified by surprise group), compute per-document Pearson r between v1 EARS and v2 LM-tagged scores. Target r > .60 for both epistemic and aleatory.

**4C — Predictive validity.** Re-run surprise -> E/A regressions on the held-out 30% with v2 counts. Required: signs preserved AND p < .05 for Negative-vs-Positive contrast in both equations.

**4D — Leave-one-out robustness.** Drop each newly tagged word; re-run 4C. No single word should flip significance.

**4E — Top-3 concentration.** < 50% of category signal from top-3 words.

## Step 5 — Deliverables

- `outputs/dictionary_v2.txt` — 297 LM words, each tagged HIGH-CONFIDENCE-EPISTEMIC / HIGH-CONFIDENCE-ALEATORY / AMBIGUOUS / [Excluded if NEITHER]
- `outputs/dictionary_v2_votes.csv` — every word, all 5 raters' votes, final tag, agreement summary
- `outputs/dictionary_v2_calibration.csv` — the 8 v1-overlap words and how each was classified
- `outputs/dictionary_v2_rejected.csv` — words tagged NEITHER, with vote pattern
- `outputs/validation_report.md` — alpha, all four validation tests, leave-one-out and top-3 tables
- `processed_data/kwic_lm297.json` — sampled corpus contexts (gitignored if large)
- `docs/expansion_protocol.md` — this document

## Reporting language (paper / OSF boilerplate)

> "We tagged the 297 words in the Loughran & McDonald (2011) 'Uncertainty' word list as primarily epistemic, primarily aleatory, ambiguous, or neither, using a 5-rater LLM ensemble (varied prompt framings at temperature 0.7), with each rater seeing five real usage contexts sampled from the earnings-call corpus. Inter-rater agreement was Krippendorff's alpha = [X]. Per-word acceptance required >= 4 of 5 raters agreeing on the same label. The method was calibrated against the 8 words appearing in both LM 297 and the prior EARS dictionary (Ulkumen, Fox & Malle 2016): [X] of 8 matched their known classifications. The resulting v2 dictionary was held-out validated on 30% of transcripts, split by firm and stratified by surprise group: convergent validity against v1 EARS (r = [X] epistemic, [X] aleatory), preserved predictive validity for the surprise -> E/A relationship (v1: beta = [X], p = [X]; v2: beta = [X], p = [X]), and per-word leave-one-out robustness. Both v1 and v2 results are reported throughout."

## What this protocol does NOT do

- **No five-method candidate generation.** LM 297 is the input; we do not search for words beyond it. If after this Option B the LM list looks insufficient, we revive the v1.0 expansion methods in a v2.1 protocol.
- **No FinBERT / embedding-based classifier.** Considered (CG-LET draft) and cut for simplicity. The calibration check via v1 EARS overlap substitutes for an independent secondary classifier.
- **No human raters.** Per design constraint. Convergent validation against the parallel Qualtrics human-rating study (`SV_ahjVK84570ekXFY`) will be added as a supplementary validation when those data are in.
- **No new construct definitions.** The Fox & Ulkumen / Tannenbaum-Fox-Ulkumen distinction in `docs/construct_definitions.md` is binding and unchanged.
- **No within-LM word reduction.** Even if some LM words look weak (high-frequency hedging modals like *could*, *may*, *might*), they stay in the input pool and get tagged honestly. If the rater ensemble decides they're NEITHER, they get dropped through that gate, not through curation.

## What not to do

- Do not iterate the dictionary after seeing held-out regression results. If v2 fails Step 4C, document the failure and stop.
- Do not silently change thresholds after seeing alpha, r, or predictive coefficients.
- Do not skip the rejection log. Every dropped word records its reason.
- Do not pre-judge LM words as "obviously aleatory" or "obviously epistemic" before running them through the rater ensemble.

## Justification for design choices (citations)

| Choice | Justification | Cite |
|---|---|---|
| LLM ensemble (5 prompts) | Stabilizes classification; outperforms any single prompt or model | Zhang et al. 2025 (arXiv 2511.15714); Sci Reports 2025 |
| Corpus-grounded contexts in-prompt | Improves LLM word-sense judgment substantially over definition-only prompts | recent WSD literature; arXiv 2503.08662 |
| 5 raters with diverse framings (vs. self-consistency same prompt) | Captures construct-relevant variance, not just sampling variance | Wang et al. 2022 ICLR (Self-Consistency); ACL 2025 |
| Krippendorff's alpha | Standard inter-rater reliability metric across LLM-as-annotator literature | Gilardi et al. 2023 PNAS |
| Held-in calibration via v1 overlap | Independent ground truth that doesn't come from the LLM | Standard methodology grounding |
| Held-out predictive validity | Tests the construct measurement on data the method never saw | Standard text-as-data practice |

## Version history

- **v1.0 (2026-04-23):** Five-method candidate generation + 5-rater LLM ensemble + held-out validation, starting from 30 v1 EARS seeds. Step 2 was executed (159 surviving candidates). Steps 3-6 paused.
- **v2.0 (2026-04-29):** Replaces v1.0. Drops candidate generation entirely. Takes the 297 LM Uncertainty words as the input pool directly. Adds calibration via v1 EARS overlap. Drops the FinBERT/embedding triangulation considered in the CG-LET draft.
