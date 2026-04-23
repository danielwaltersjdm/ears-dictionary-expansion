# CLAUDE.md - EARS Dictionary Expansion

## Research goal

Expand and validate the Epistemic-Aleatory Rating Scale (EARS) word dictionary used to score earnings-call transcripts, producing a v2 dictionary that is:

1. Triangulated across multiple candidate-generation methods (not just corpus collocation)
2. Validated by LLM-ensemble classification with inter-rater reliability statistics
3. Construct-validity tested on held-out transcripts and cross-corpus samples
4. Fully documented, versioned, and reproducible

The original 30-word v1 dictionary (Tannenbaum / Fox / Uelkuemen tradition) is frozen as baseline. All analyses will report v1 and v2 side by side.

## Constructs

- **Epistemic uncertainty:** uncertainty in principle reducible via additional knowledge, analysis, or effort. Outcome is framed as *knowable*.
- **Aleatory uncertainty:** uncertainty that is intrinsically random and irreducible even with perfect information. Outcome is framed as *stochastic*.

Canonical reference: Fox & Uelkuemen (2011); Tannenbaum, Fox & Uelkuemen (2017). Full operational definitions are in `docs/construct_definitions.md`.

## Architecture

```
EARS Dictionary Expansion/
  CLAUDE.md                    stable project knowledge (this file)
  STATE.md                     living task tracker
  requirements.txt             pinned Python deps
  .gitignore
  raw_data/                    NOT tracked in git; large .dta sits at:
                               ../Variants of Uncertainty/Credit Blame/
                               Earnings Calls Language/0100_ECT.dta  (~876 MB)
                               ../Variants of Uncertainty/Credit Blame/
                               Earnings Calls Language/0500_es_ect_results_language.dta
  processed_data/              stripped text, candidate pools, KWIC windows
  outputs/                     dictionaries, validation reports, figures
    dictionary_v1.txt          FROZEN - do not modify
    dictionary_v2.txt          expanded, with bigram constraints
    candidate_pool.csv         every candidate + provenance + rater votes
    rejection_log.csv          dropped candidates + reasons
    validation_report.md       alpha, convergent r, predictive stats
  scripts/                     Python pipeline modules
    sync_to_osf.py             post-push OSF sync (auto)
  docs/                        reference material
    construct_definitions.md
    expansion_protocol.md
  sessions/                    per-session logs, YYYY-MM-DD
```

## Key data sources

| File | Location | Role |
|---|---|---|
| `0100_ECT.dta` | `../Variants of Uncertainty/Credit Blame/Earnings Calls Language/` | Raw transcripts (~16k calls, HTML for P1/P2/P3, per-word counts for all 30 v1 dictionary terms) - Stata format 118 |
| `0500_es_ect_results_language.dta` | (same folder) | Analysis-ready aggregated, 13,092 rows, merged with IBES/CRSP - Stata format 113 |
| Loughran-McDonald master dictionary | `processed_data/LoughranMcDonald_MasterDictionary.csv` | External financial lexicon for Method 3 candidate sourcing |

Raw data is NOT version-controlled or OSF-synced. Paths are referenced from this project; all code reads data from the external location.

## Conventions

- **Dictionary v1 is frozen.** Every comparison reports v1 alongside v2. Do not modify `dictionary_v1.txt`.
- **Pre-commit thresholds before computing outcomes.** Every acceptance rule (rater agreement, convergent r, predictive p-value) is written to `docs/expansion_protocol.md` before the computation that produces the value.
- **Held-out validation.** Transcripts are split 70/30 by firm (IDPERMNO), stratified by surprise group. Development uses 70%; validation uses the held-out 30%.
- **LLM ensemble rating.** No human raters. 5 Claude calls per candidate with varied prompt framings at temperature 0.7. Krippendorff's alpha reported across the ensemble.
- **All candidate decisions logged.** `candidate_pool.csv` records every candidate, its method provenance, its 5 ratings, and its accept/reject outcome. Rejected candidates carry a reason.

## Environment notes

- Python: `C:/Users/dwalters1/Dropbox/projects/EARS Dictionary Expansion/venv/Scripts/python.exe`
  - Create with: `python -m venv venv` (using the Anaconda python at `C:/Users/dwalters1/AppData/Local/anaconda3/python.exe`)
- Required packages: `pandas numpy scipy gensim nltk beautifulsoup4 lxml requests tqdm krippendorff pyreadstat anthropic`
- Tulane proxy: all `requests` calls use `verify=False` with `urllib3.disable_warnings()`; curl uses `--insecure`
- OSF token stored in `.git/hooks/post-push` (per user CLAUDE.md convention)
- GitHub repo: `github.com/danielwaltersjdm/ears-dictionary-expansion`
- OSF node: see `STATE.md` for ID

## Protocol version

v1.0 of the expansion protocol is in `docs/expansion_protocol.md`. It was committed before the LLM-rating step was executed. Any changes to the protocol mid-pipeline create a new version; old versions remain in git history.

## Relation to prior work

- Parent project: "Variants of Uncertainty" at `../Variants of Uncertainty/` (older, non-git tree)
- The v1 dictionary and `0100_ECT.dta` were produced for the earnings-surprise -> E/A language study. The replication was confirmed on 2026-04-22 (negative surprise -> epistemic language, positive surprise -> aleatory language, both significant).
- This project extends that measurement instrument; it does not revise the original findings.
