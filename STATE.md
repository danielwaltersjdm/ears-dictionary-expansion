# STATE - EARS Dictionary Expansion

Last updated: 2026-04-23

## Done

- Replication of main surprise -> E/A result on `0500_es_ect_results_language.dta` (confirmed by prior Claude session on 2026-04-22)
- Discovered `0100_ECT.dta` raw transcript file with full HTML and per-word counts for all 30 dictionary terms
- Wrote expansion protocol (five-method candidate generation, five-LLM-rater ensemble, held-out construct validation) - frozen in `docs/expansion_protocol.md`
- Froze v1 dictionary in `outputs/dictionary_v1.txt`
- Wrote construct definitions in `docs/construct_definitions.md`
- Set up project: git repo, GitHub remote, OSF node, post-push sync hook
  - GitHub: https://github.com/danielwaltersjdm/ears-dictionary-expansion
  - OSF: https://osf.io/bc9u5/
- Initial commit + push done; 9 files synced to OSF.
- Note: git has no native `post-push` hook. Until a shell-level `git push` wrapper is in place, sync must be invoked manually after each push:
  ```
  export OSF_TOKEN="..."
  /c/Users/dwalters1/AppData/Local/anaconda3/python.exe "/c/Users/dwalters1/Dropbox/projects/EARS Dictionary Expansion/scripts/sync_to_osf.py"
  ```
  Or: convert `.git/hooks/post-push` to `.git/hooks/pre-push` (fires natively before upload).
- Located the source paper for v1 dictionary: Ulkumen, Fox, & Malle (2016), "Two dimensions of subjective uncertainty: Clues from natural language," *JEP:General*, 145(10), 1280-1297. Manuscript draft and original lexicon spreadsheet copied to `docs/`:
  - `docs/UlkumenFox&Malle-2-8-15 - DW comments.docx` -- Feb 2015 manuscript draft with DW's comments (predates publication)
  - `docs/Language list lexicon.xlsx` -- the working lexicon spreadsheet (3 sheets: raw lists, combined, and Aleatory/Epistemic-tagged Sheet3)
  - **Notable discrepancy:** Sheet 3 lists 15 epistemic + 14 aleatory + extras (`chances`, `supposedly`, `Random`) that are not in the frozen v1 dictionary. Worth investigating why these were dropped between the original lexicon and v1.

## In progress

- Other Claude session ran Steps 1-2 (v1 freeze + definitions, five-method candidate pool generation). Step 2 produced 159 surviving candidates; output at `outputs/candidate_pool.csv` and `outputs/rejection_log.csv`. Steps 3-6 NOT executed.

## Adopted (2026-04-28)

- **Base wordlist:** Loughran-McDonald (2011) "Uncertainty" — 297 words. Frozen, citable, derivation documented in `docs/wordlist_derivation.md`. Filtered file at `outputs/loughran_mcdonald_uncertainty_297.csv`.
- v2 expansion work paused. May resume if needed; for now LM is the base.

## Next

- Step 3: LLM ensemble classification of candidates that survive Step 2 triangulation
- Step 4: polysemy handling (bigram constraints for ambiguous survivors)
- Step 5: held-out construct-validity validation (70/30 split by firm)
- Step 6: finalize dictionary_v2.txt, validation_report.md
- OSF registration of expansion_protocol.md (timestamp lock) before Step 3 executes

## Blocked

- None currently.

## Open questions

- Is an OpenAI or Gemini API key available for multi-model ensemble, or should we stick with Claude-only (5 prompt variants)? Current plan: Claude-only.
- Cross-corpus validation (Step 5E): FOMC minutes vs analyst reports vs IPCC excerpts - which is most appropriate? Current plan: FOMC minutes if time permits.
- Should analyst questions in P3 be separated from manager responses during candidate discovery? Current plan: yes, tag by speaker role where possible.
