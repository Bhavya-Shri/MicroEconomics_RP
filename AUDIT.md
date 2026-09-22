# Audit log

This file records what was changed while turning the civil-engineering jarosite review into a computer-science draft, and why. Entries are added as the work proceeds.

## Sources the new draft does not treat as its own results

The starting document is the unpublished review *Reusing Hazardous Industrial Waste as a Sustainable Concrete Material* (Tarun Kumar P, Elavenil S, Raja Rajeswari G, Jayaraj R). That file was read from the local `.docx`. It is a literature review. It does not report a new casting programme, a dataset, or a fitted model.

No other uploaded paper files were present in this workspace when the draft was built. The GitHub repository `Bhavya-Shri/MicroEconomics_RP` was empty. Numbers used below were taken from open papers and public statistical pages, and each row in `data/literature_mixes.csv` names its source.

## Loopholes in the first draft, and the correction

| Loophole | Correction in this repository |
| --- | --- |
| The abstract states a 17% strength gain at 15% jarosite as the paper's result. That figure is attributed to Gared and Gaur and is not in their open abstract. | The 17% / 17.88% figure is not used. Strength is taken only from tables or sentences that state both the mix result and the control, or an explicit percentage versus the control. |
| Cited studies disagree, and the review quotes the favourable case. | Model 1 is fit separately by study and on the pooled 28-day sample. Both curves are reported. |
| No methodology and no data table that can be re-run. | `data/literature_mixes.csv` is the dataset. `src/run_models.py` refits both models. |
| "Predict the economy" has no price, boundary, or pollution rule. | Model 2 is an accounting model per tonne of jarosite, then a supply upper bound. It is not a GDP forecast. |
| Leaching is discussed after strength and is not a condition of the conclusion. | A mix with no leaching test is marked `untested`. Benefit figures for those mixes are conditional on compliance. A failed screen zeroes the recycling credit. |
| India zinc output is given as 2.5 lakh tonnes. USGS primary smelter output is about 0.82 million tonnes in 2024. | The flow account uses USGS 2024 primary smelter production. |
| The circular-economy section mixes in red mud. | Red mud is not part of this paper. |
| Duplicate references, two section 2s, and a broken abrasion paragraph. | Those passages are not carried forward. |
| Jarofix stabilisation already uses cement and lime before landfill (Gared and Gaur abstract: 2% lime and 10% cement). | Model 2 has a switch for that avoided stabilisation cement so it is not silently ignored or double-counted. |
| USEPA "limits" in the review table include zinc, copper, and iron, which are not the classic TCLP toxicity-characteristic list. | The screen uses the toxicity-characteristic levels for lead (5 mg/L), cadmium (1 mg/L), and silver (5 mg/L). Other metals are not given invented limits. |

## Change log

- 2026-09-22: Read the `.docx` review and wrote a working plain-text extract (`_draft_extract.txt`, not part of the paper).
- 2026-09-22: Confirmed the workspace had no additional uploaded papers and the GitHub repo was empty.
- 2026-09-22: Built `data/literature_mixes.csv` from Sharma (JETIR 2021), Nandi and Ransinchung (IOP 2021), and Afaque et al. (E3S 2024), with a source column on every row.
- 2026-09-22: Added `data/parameters.json` for prices, the jarosite factor, zinc output, and carbon scenarios. Disposal and transport costs are marked as assumptions.
- 2026-09-22: Implemented Model 1 and Model 2 in `src/run_models.py`.
- 2026-09-22: Ran `python src/run_models.py`. Leave-one-study-out \(R^2\) was negative in five of six model–study pairs (the exception was the random forest on the Nandi hold-out, \(R^2\) 0.11). The draft reports that failure instead of a portable accuracy claim.
- 2026-09-22: Central benefit at a shared strength pass is Rs 8,000 per tonne, equal to the central retail cement price, because carbon, disposal, and transport are zero unless a scenario turns them on. A leaching failure returns Rs 0. All 40 compiled rows are `untested` for leaching.
- 2026-09-22: Wrote `paper/DRAFT.md` (abstract, introduction, methodology, results, conclusion) and `README.md`.
- 2026-09-22: Did not carry forward the 17% / 17.88% strength sentence, the red-mud paragraphs, the duplicated references, or the Word leaching table. Gared and Gaur are cited only for the jarofix recipe in their abstract (2% lime and 10% cement).
- 2026-09-22: Pushed `main` to https://github.com/Bhavya-Shri/MicroEconomics_RP.git.
