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

## In progress

- Other Claude session running Step 1 (v1 freeze + definitions) and Step 2 (five-method candidate pool generation)

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
