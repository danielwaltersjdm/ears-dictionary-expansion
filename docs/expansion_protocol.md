# EARS Dictionary v2 Expansion Protocol

**Version:** 1.0
**Frozen:** 2026-04-23
**Binding:** This document is committed to git (and registered on OSF) before Step 3 executes. Any change after Step 3 starts creates a new version; the original remains in git history as the pre-committed protocol.

## Purpose

Expand the 30-word EARS v1 dictionary to a validated v2, using only LLM-based validation (no human raters). Report v1 and v2 side-by-side in all downstream analyses.

## Binding constraints

- Dictionary v1 is frozen. Do not modify.
- All acceptance thresholds are set in this document BEFORE the value they gate is computed.
- Candidate discovery and validation use different data (70/30 split by firm).
- Every decision is logged; every rejected candidate carries a reason.

---

## Step 1 - Freeze v1 and construct definitions (15 min)

- `outputs/dictionary_v1.txt` - frozen
- `docs/construct_definitions.md` - frozen
- These are the acceptance gate for all subsequent candidate classification.

## Step 2 - Generate candidate pool via five independent methods (90 min)

**Method 1 - Corpus collocations.** Top 50 unigrams + top 30 bigrams within +-5 tokens of each v1 seed in stripped P2+P3 text. Min corpus frequency 50. Stop-words removed.

**Method 2 - Corpus word2vec.** Train gensim word2vec on stripped P2+P3 (size=100, window=5, min_count=10). Top-20 cosine neighbors per v1 seed. Union across seeds.

**Method 3 - Loughran-McDonald financial lexicon.** Include all words flagged `Uncertainty` or `Modal_Weak` in the LM master dictionary as candidates.

**Method 4 - WordNet expansion.** For each v1 seed, pull synonyms and direct hyponyms via `nltk.corpus.wordnet`.

**Method 5 - LLM theory-driven brainstorm.** Single Claude call: given the construct definitions, generate 30 candidate words and 20 candidate phrases per construct, grounded in Fox & Uelkuemen (2011) and subsequent EARS work.

**Triangulation rule:** entry to Step 3 requires flagging by >= 2 independent methods. Single-method candidates go to `rejection_log.csv` with reason `insufficient_triangulation`. v1 words auto-carry.

**Output:** `outputs/candidate_pool.csv` with columns: `candidate`, `type` (word/phrase), `methods` (list), `n_methods`, `corpus_frequency`.

## Step 3 - LLM ensemble classification (60 min)

For each triangulated candidate, run 5 independent Claude calls with varied prompts. Each returns one label: EPISTEMIC / ALEATORY / AMBIGUOUS / NEITHER.

- **Prompt A (strict, zero-shot)**
- **Prompt B (chain-of-thought)**
- **Prompt C (expert frame - behavioral economist)**
- **Prompt D (conservative - bias toward AMBIGUOUS)**
- **Prompt E (phrase-context-aware)**

Each at temperature 0.7, N=1 draw each => 5 labels per candidate.

Compute Krippendorff's alpha across the 5 raters on the full candidate set. Report alpha in `outputs/validation_report.md`.

**Acceptance rule (pre-committed):**
- ACCEPT if >= 4 of 5 raters agree on EPISTEMIC or on ALEATORY
- REJECT if >= 2 raters return NEITHER or AMBIGUOUS
- FLAG for adjudication (human review) otherwise (3/5 majority)

## Step 4 - Polysemy handling (30 min)

For each accepted candidate, sample 20 random context windows from the corpus. Single Claude call per window: "Is `{candidate}` used in the [accepted] construct sense here? Yes/No." If < 70% yes, require a bigram constraint: identify 2-3 disambiguating co-words that preserve the sense. Record in `dictionary_v2.txt` as `candidate [bigram:X,Y,Z]`.

## Step 5 - Held-out construct-validity validation (60 min)

Split transcripts 70/30 by firm (`IDPERMNO`), stratified by `surprise` group (negative/neutral/positive). Develop v2 on 70%; validate on 30%.

**Pre-committed thresholds:**

- **5A - Convergent validity.** Per-document Pearson r between v1 and v2 scores (epistemic and aleatory separately) on held-out sample. Accept if r > 0.7. Flag if r < 0.5.
- **5B - Predictive validity.** Re-run `regress epistemic i.surprise, cluster(IDPERMNO)` and aleatory equivalent on held-out 30% with v1 and v2. Accept v2 if sign is preserved AND p-value stays below .05 for Neutral-vs-Negative AND Positive-vs-Negative contrasts in both dependent variables.
- **5C - Leave-one-out robustness.** Drop each newly added v2 word one at a time; re-run 5B. No single added word should flip significance.
- **5D - Top-k concentration.** Compute % of total epistemic and aleatory counts contributed by the top 3 words. Flag as brittle if > 50%.
- **5E - Cross-corpus sanity check (optional, time permitting).** Score 10 FOMC minutes with v2. Eyeball E/A values for plausibility.

## Step 6 - Deliverables

- `outputs/dictionary_v1.txt` (frozen)
- `outputs/dictionary_v2.txt` (final, with bigram constraints)
- `outputs/candidate_pool.csv`
- `outputs/rejection_log.csv`
- `outputs/validation_report.md`
- `docs/construct_definitions.md`
- `docs/expansion_protocol.md` (this file, timestamped)
- `sessions/session-YYYY-MM-DD.md` (per-session log)

## Reporting language (boilerplate for papers / OSF)

> "Dictionary expansion was conducted post hoc using a five-method candidate-generation pipeline (corpus collocation, corpus-trained word2vec, Loughran-McDonald financial lexicon, WordNet expansion, and LLM theory-driven brainstorm). Candidates flagged by >= 2 independent methods were classified by a 5-rater LLM ensemble (varied prompt framings at temperature 0.7), with Krippendorff's alpha = [X]. Acceptance required >= 4/5 rater agreement. Dictionary was developed on 70% of transcripts and validated on a 30% held-out sample; predictive validity of the surprise -> E/A relationship was preserved (v1: beta = [X], p = [X]; v2: beta = [X], p = [X]). Both v1 and v2 results are reported for transparency."

## What not to do

- Do not iterate the dictionary after seeing held-out regression results. If v2 fails Step 5B, document the failure and stop - do not tweak until it passes.
- Do not drop v1 words in the course of building v2. v1 stays frozen as the baseline.
- Do not silently change thresholds after seeing alpha or r or predictive coefficients.
- Do not skip the rejection log. Every dropped candidate is recorded with a reason.
