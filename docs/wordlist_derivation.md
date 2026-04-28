# Base Wordlist for the EARS Dictionary Expansion — Derivation

**Date frozen:** 2026-04-28
**Status:** Adopted as the base/reference wordlist. Will be the citable starting point for any v2 work.

## Decision

The 297-word **Loughran-McDonald (2011) "Uncertainty"** category is adopted as the base lexicon for our uncertainty-language work. Earlier candidates (Ulkumen-Fox-Malle 2016 EARS list of 30 words; the in-house "Language list lexicon.xlsx"; several Budescu papers) were considered but rejected for the reasons documented below.

## Citation

> Loughran, T., & McDonald, B. (2011). When is a liability not a liability? Textual analysis, dictionaries, and 10-Ks. *Journal of Finance*, 66(1), 35–65. https://doi.org/10.1111/j.1540-6261.2010.01625.x

The lexicon itself is updated periodically and hosted at the University of Notre Dame Software Repository for Accounting and Finance:
https://sraf.nd.edu/loughranmcdonald-master-dictionary/

The version used here is the Master Dictionary 1993-2025 build (~86,553 words × 17 columns). Free for academic use; commercial licensing separate.

## Derivation procedure (exact, reproducible)

1. Downloaded the Loughran-McDonald Master Dictionary as a single CSV from the Notre Dame SRAF page (Google Drive file ID `1iq2RUf8qGFEAk1g8wQntP3habOnR3fXF`, retrieved 2026-04-23).
2. Filtered the master CSV for rows where the `Uncertainty` column is greater than zero.
3. Lowercased all words; sorted alphabetically.
4. Output: 297 words.

The Python operation, in full:

```python
import pandas as pd
df = pd.read_csv("LoughranMcDonald_MasterDictionary.csv")
unc = df[df["Uncertainty"] > 0].copy()
unc["Word"] = unc["Word"].str.lower()
unc.sort_values("Word")[["Word", "Word Count", "Doc Count", "Average Proportion"]] \
   .to_csv("outputs/loughran_mcdonald_uncertainty_297.csv", index=False)
```

The filtered file is at `outputs/loughran_mcdonald_uncertainty_297.csv`. The full master CSV (which is large, gitignored, and not on OSF) is at `processed_data/LoughranMcDonald_MasterDictionary.csv`.

## Why this list, not the alternatives

| Candidate | Size | Status | Why not (or yes) |
|---|---|---|---|
| **Loughran-McDonald (2011) "Uncertainty"** | 297 | **Adopted** | Peer-reviewed in *Journal of Finance*; purpose-built for financial text (10-Ks, earnings calls); free for academic use; downloadable as a single CSV; widely cited; broad enough to support real measurement |
| Ulkumen, Fox & Malle (2016) EARS list | 30 | Retained as construct anchor only | Too small for primary measurement; will be reported alongside as v1 baseline |
| In-house `Language list lexicon.xlsx` | ~50 phrases + 30 words | Retained as historical reference | Mixed sources, undocumented derivation, includes verbal-probability phrases (different construct from EARS) |
| Budescu & Wallsten (1985) | ~19 phrases (cited count) | Rejected | Could not retrieve original PDF; secondary sources do not reproduce the stimulus list; the 19-item count match in our in-house lexicon is circumstantial and the content profile (frequency adverbs vs. probability phrases) is atypical for that paper |
| Wallsten et al. (1986) | 18 phrases | Not pursued | Smaller than LM; verbal-probability magnitude focus, not E/A construct |
| IPCC verbal probability scale | 7 phrases | Not pursued for base list | Probability magnitude only; useful for a separate calibration axis if needed later |
| LIWC `tentat`/`certain` | proprietary | Not pursued | Proprietary license; less directly comparable to LM |
| Mosteller & Youtz (1990) | ~25 phrases | Not pursued | Older; verbal-probability magnitude focus |

## Limitations of the LM "Uncertainty" list (documented for transparency)

- **Flat category.** Loughran-McDonald flags words as "Uncertainty" but does not distinguish epistemic from aleatory. This is a feature, not a bug, for a base list, but means the E/A split must be re-imposed downstream if needed.
- **Inflectional density.** ~30% of the 297 words are morphological variants of the same root (e.g., `anticipate`, `anticipated`, `anticipates`, `anticipating`, `anticipation`, `anticipations`). Some analyses will want to lemmatize before counting; others will want to keep the inflections separate.
- **Domain.** Built on the 10-K filing corpus. Some words (`abeyance`, `unhedged`, `unguaranteed`) are financial-document-typical and may be rare in other genres.
- **Hedging modals included.** `could`, `may`, `might`, `perhaps`, `possibly`, `probably`, `seemingly`, `somewhat` are all in the list. These are very high-frequency in any English text and may dominate counts unless contextual filtering is applied.
- **Some construct gaps.** `expect`, `random`, and `likely` appear in our v1 EARS list but `expect` and `likely` are NOT in LM "Uncertainty"; `random` IS in LM. Worth noting because v1 was derived from a different theoretical lens (Ulkumen-Fox-Malle) and the two lists have only partial overlap.

## Practical note on use

If the next analysis is dictionary-counting on earnings-call transcripts: the LM list can be applied directly to the existing pre-processed corpus (`processed_data/stripped_corpus.txt.gz`) using simple word-count code. No further preprocessing is needed.

If the next analysis is human/LLM rating of words for E/A split: the 297-word list is the candidate pool and will need a classification step (handled by the protocol in `expansion_protocol.md`).

The file `outputs/loughran_mcdonald_uncertainty_297.csv` is the canonical reference. Any downstream work cites *that* file plus the Loughran-McDonald 2011 paper.
