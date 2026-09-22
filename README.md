# Jarosite recycling models

Computational draft that replaces a civil-engineering review of jarosite in concrete. The paper is `paper/DRAFT.md`. The change record is `AUDIT.md`.

Model 1 scores whether published jarosite mixes keep compressive strength relative to their own control. Model 2 converts a strength-feasible tonne into a cement-value benefit and sets that benefit to zero if a leaching screen fails. The benefit is not a GDP forecast.

```text
python src/run_models.py
```

Outputs land in `outputs/`: `results.json`, `benefit_by_replacement.csv`, `benefit_sensitivity.csv`, and `strength_ratio_28d.png`.

Inputs are `data/literature_mixes.csv` and `data/parameters.json`. Prices that are assumptions are marked in the parameter file. Do not add a strength or a leachate number without a source note in the CSV.
