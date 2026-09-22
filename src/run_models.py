"""Two models for jarosite recycling.

Model 1 predicts the compressive-strength ratio of a jarosite mix relative to
its own control. Model 2 turns a strength-feasible, leaching-screened tonne of
jarosite into a cement-saving benefit. It does not forecast GDP.

Run from the repository root:

    python src/run_models.py
"""

from __future__ import annotations

import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "literature_mixes.csv"
PARAMS = ROOT / "data" / "parameters.json"
OUT = ROOT / "outputs"


def load_inputs():
    mixes = pd.read_csv(DATA)
    with PARAMS.open(encoding="utf-8") as handle:
        params = json.load(handle)
    return mixes, params


def feature_frame(frame: pd.DataFrame) -> np.ndarray:
    replacement = frame["replacement_pct"].to_numpy(dtype=float)
    curing = frame["curing_days"].to_numpy(dtype=float)
    return np.column_stack([replacement, replacement ** 2, curing])


def regression_metrics(y_true, y_pred) -> dict:
    y_true = np.asarray(y_true, dtype=float)
    y_pred = np.asarray(y_pred, dtype=float)
    return {
        "n": int(len(y_true)),
        "mae": float(mean_absolute_error(y_true, y_pred)),
        "rmse": float(np.sqrt(mean_squared_error(y_true, y_pred))),
        "r2": float(r2_score(y_true, y_pred)),
    }


def leave_one_study_out(compressive: pd.DataFrame) -> list[dict]:
    """Hold out each laboratory study. Controls stay in the held-out fold."""
    rows = []
    for study in sorted(compressive["study_id"].unique()):
        train = compressive[compressive["study_id"] != study]
        test = compressive[compressive["study_id"] == study]
        x_train, y_train = feature_frame(train), train["strength_ratio"].to_numpy(dtype=float)
        x_test, y_test = feature_frame(test), test["strength_ratio"].to_numpy(dtype=float)

        linear = LinearRegression()
        linear.fit(x_train, y_train)
        forest = RandomForestRegressor(
            n_estimators=200,
            max_depth=3,
            min_samples_leaf=2,
            random_state=0,
        )
        forest.fit(x_train, y_train)
        for name, model in (("quadratic_linear", linear), ("random_forest", forest)):
            scored = regression_metrics(y_test, model.predict(x_test))
            scored["model"] = name
            scored["held_out_study"] = study
            rows.append(scored)
    return rows


def fit_quadratic_curve(frame: pd.DataFrame) -> dict:
    """ratio = a + b*replacement + c*replacement^2, at one curing age."""
    replacement = frame["replacement_pct"].to_numpy(dtype=float)
    y = frame["strength_ratio"].to_numpy(dtype=float)
    x = np.column_stack([np.ones(len(frame)), replacement, replacement ** 2])
    coefficients, *_ = np.linalg.lstsq(x, y, rcond=None)
    grid = np.arange(0, 31, 1, dtype=float)
    fitted = coefficients[0] + coefficients[1] * grid + coefficients[2] * grid ** 2
    peak_at = int(grid[int(np.argmax(fitted))])
    return {
        "intercept": float(coefficients[0]),
        "linear_term": float(coefficients[1]),
        "quadratic_term": float(coefficients[2]),
        "fitted_peak_replacement_pct": peak_at,
        "fitted_peak_ratio": float(fitted[peak_at]),
        "curve": {str(int(level)): float(value) for level, value in zip(grid, fitted)},
    }


def leaching_screen(sample: dict | None, limits: dict) -> str:
    """Return pass, fail, or untested.

    sample maps a metal symbol to a concentration in mg/L. Missing metals,
    or a missing sample, stay untested. A metal that is not in `limits` is
    ignored rather than given a made-up threshold.
    """
    if not sample:
        return "untested"
    seen = False
    for metal, limit in limits.items():
        if metal not in sample or sample[metal] is None:
            continue
        seen = True
        if float(sample[metal]) > float(limit):
            return "fail"
    return "pass" if seen else "untested"


def cement_credit_tonnes(strength_ratio: float, threshold: float, rule: str) -> float:
    if rule == "threshold":
        return 1.0 if strength_ratio >= threshold else 0.0
    if rule == "proportional":
        return float(min(1.0, max(strength_ratio, 0.0)))
    raise ValueError(rule)


def inr(value: float) -> float:
    return float(round(value, 2))


def benefit_per_tonne(
    strength_ratio: float,
    leaching_status: str,
    params: dict,
    cement_price: float,
    carbon_price: float,
    disposal_cost: float,
    transport_cost: float,
    co2_factor: float,
    include_jarofix_cement: bool,
    rule: str,
) -> dict:
    """Indian rupees per tonne of jarosite placed in concrete as cement replacement.

    A failed leaching screen zeroes every credit. An untested mix keeps the
    arithmetic but is flagged so it is not read as environmental clearance.
    """
    failed = leaching_status == "fail"
    credit = 0.0 if failed else cement_credit_tonnes(
        strength_ratio, params["strength_ratio_threshold"], rule
    )
    # The jarofix cement credit is the cement already added before landfill.
    # It is separate from the concrete replacement credit, and it is off unless
    # the caller turns it on. A leaching failure removes both credits.
    jarofix_cement = 0.0
    if include_jarofix_cement and not failed:
        jarofix_cement = params["jarofix_cement_t_per_t_jarosite"]
    cement_tonnes = 0.0 if failed else credit + jarofix_cement

    cement_value = 0.0 if failed else cement_tonnes * cement_price
    carbon_value = 0.0 if failed else cement_tonnes * co2_factor * carbon_price
    disposal_value = 0.0 if failed else disposal_cost
    haul = 0.0 if failed else transport_cost
    net = 0.0 if failed else cement_value + carbon_value + disposal_value - haul

    return {
        "leaching_status": leaching_status,
        "strength_ratio": float(strength_ratio),
        "cement_displaced_t": float(cement_tonnes),
        "cement_value_inr": inr(cement_value),
        "carbon_value_inr": inr(carbon_value),
        "disposal_value_inr": inr(disposal_value),
        "transport_cost_inr": inr(haul),
        "net_inr_per_t": inr(net),
        "conditional_on_leaching_compliance": leaching_status != "pass",
    }


def observed_28_day(compressive: pd.DataFrame) -> pd.DataFrame:
    return compressive[compressive["curing_days"] == 28].copy()


def agreement_table(day28: pd.DataFrame, threshold: float) -> list[dict]:
    """At each replacement tested by both Sharma and Nandi, record both ratios."""
    studies = ["sharma2021", "nandi2021"]
    present = day28[day28["study_id"].isin(studies)]
    levels = sorted(
        set(present[present["study_id"] == "sharma2021"]["replacement_pct"])
        & set(present[present["study_id"] == "nandi2021"]["replacement_pct"])
    )
    rows = []
    for level in levels:
        ratios = {}
        for study in studies:
            match = present[
                (present["study_id"] == study) & (present["replacement_pct"] == level)
            ]
            ratios[study] = float(match["strength_ratio"].iloc[0])
        both_pass = all(value >= threshold for value in ratios.values())
        rows.append(
            {
                "replacement_pct": int(level),
                "sharma2021_ratio": ratios["sharma2021"],
                "nandi2021_ratio": ratios["nandi2021"],
                "both_at_least_control": both_pass,
                "leaching_status": "untested",
            }
        )
    return rows


def scale_supply(net_per_tonne: float, params: dict) -> dict:
    zinc = params["zinc_primary_smelter_t_2024"]
    factor = params["jarosite_t_per_t_zinc"]
    kangas = zinc * factor
    already = params["hzl_jarosite_used_in_cement_construction_t"]
    incremental = max(0.0, kangas - already)
    supplies = {
        "kangas_factor_on_usgs_2024_smelter": kangas,
        "incremental_after_hzl_reported_use": incremental,
    }
    for item in params["alternate_jarosite_supply_tpy"]:
        supplies[item["name"]] = item["tonnes"]
    return {
        name: {
            "jarosite_t": float(tonnes),
            "gross_cement_credit_inr": inr(tonnes * net_per_tonne),
        }
        for name, tonnes in supplies.items()
    }


def plot_ratios(day28: pd.DataFrame, path: Path) -> None:
    fig, ax = plt.subplots(figsize=(7.2, 4.4))
    labels = {
        "sharma2021": "Sharma 2021, pavement concrete",
        "nandi2021": "Nandi and Ransinchung 2021, pavers",
    }
    for study, label in labels.items():
        part = day28[day28["study_id"] == study].sort_values("replacement_pct")
        ax.plot(part["replacement_pct"], part["strength_ratio"], marker="o", label=label)
    ax.axhline(1.0, color="black", linewidth=0.8, linestyle="--", label="Equal to control")
    ax.set_xlabel("Jarosite replacement of cement (%)")
    ax.set_ylabel("28-day compressive strength / control")
    ax.set_title("Observed strength ratio by study")
    ax.set_xlim(-1, 32)
    ax.legend(frameon=False)
    fig.tight_layout()
    fig.savefig(path, dpi=150)
    plt.close(fig)


def check_leaching_examples(limits: dict) -> None:
    """These are not observations. They only check the screen."""
    assert leaching_screen(None, limits) == "untested"
    assert leaching_screen({"Pb": 4.9, "Cd": 0.9, "Ag": 4.9}, limits) == "pass"
    assert leaching_screen({"Pb": 5.1, "Cd": 0.1}, limits) == "fail"
    assert leaching_screen({"Zn": 400}, limits) == "untested"


def main() -> None:
    OUT.mkdir(exist_ok=True)
    mixes, params = load_inputs()
    check_leaching_examples(params["tclp_limits_mg_per_l"])

    compressive = mixes[mixes["property"] == "compressive"].copy()
    held_out = leave_one_study_out(compressive)

    day28 = observed_28_day(compressive)
    curves = {
        study: fit_quadratic_curve(day28[day28["study_id"] == study])
        for study in ("sharma2021", "nandi2021")
    }
    agreement = agreement_table(day28, params["strength_ratio_threshold"])

    # Central benefit uses the threshold rule, published cement price only,
    # no assumed disposal or transport, no carbon price, and no jarofix credit.
    central_rows = []
    for row in agreement:
        # The tonne is useful on the strength rule only when both studies agree.
        ratio_for_credit = 1.0 if row["both_at_least_control"] else 0.0
        central = benefit_per_tonne(
            strength_ratio=ratio_for_credit,
            leaching_status=row["leaching_status"],
            params=params,
            cement_price=params["cement_price_inr_per_t"]["central"],
            carbon_price=params["carbon_price_inr_per_t"]["none"],
            disposal_cost=params["disposal_cost_inr_per_t_assumed"]["none"],
            transport_cost=params["transport_processing_inr_per_t_assumed"]["none"],
            co2_factor=params["cement_co2_t_per_t_central"],
            include_jarofix_cement=False,
            rule="threshold",
        )
        central["replacement_pct"] = row["replacement_pct"]
        central["sharma2021_ratio"] = row["sharma2021_ratio"]
        central["nandi2021_ratio"] = row["nandi2021_ratio"]
        central["both_at_least_control"] = row["both_at_least_control"]
        central_rows.append(central)

    passing = [row for row in central_rows if row["both_at_least_control"]]
    # 15% is inside the passing set for these two studies. Use it as the
    # worked example because both ratios are above 1 and it is the highest
    # shared passing level, so it diverts more jarosite per cubic metre.
    worked = max(passing, key=lambda row: row["replacement_pct"])
    supply = scale_supply(worked["net_inr_per_t"], params)

    sensitivities = []
    base_ratio = 1.0
    cases = [
        ("central_cement_only", 8000, 0, 0, 0, 0.68, False),
        ("low_cement_price", 7400, 0, 0, 0, 0.68, False),
        ("high_cement_price", 8600, 0, 0, 0, 0.68, False),
        ("carbon_500", 8000, 500, 0, 0, 0.68, False),
        ("carbon_2000", 8000, 2000, 0, 0, 0.68, False),
        ("carbon_2000_high_factor", 8000, 2000, 0, 0, 0.90, False),
        ("disposal_1500", 8000, 0, 1500, 0, 0.68, False),
        ("disposal_4000", 8000, 0, 4000, 0, 0.68, False),
        ("transport_500", 8000, 0, 0, 500, 0.68, False),
        ("transport_2000", 8000, 0, 0, 2000, 0.68, False),
        ("with_jarofix_cement_credit", 8000, 0, 0, 0, 0.68, True),
        ("leaching_fail_zeroes_credit", 8000, 0, 0, 0, 0.68, False),
    ]
    for name, price, carbon, disposal, transport, co2, jarofix in cases:
        status = "fail" if name.startswith("leaching_fail") else "untested"
        item = benefit_per_tonne(
            base_ratio,
            status,
            params,
            price,
            carbon,
            disposal,
            transport,
            co2,
            jarofix,
            "threshold",
        )
        item["case"] = name
        sensitivities.append(item)

    results = {
        "n_rows": int(len(mixes)),
        "n_compressive_rows": int(len(compressive)),
        "studies": sorted(compressive["study_id"].unique().tolist()),
        "leaching_counts": mixes["leaching_status"].value_counts().to_dict(),
        "leave_one_study_out": held_out,
        "quadratic_28_day": curves,
        "agreement_28_day": agreement,
        "central_benefit_by_replacement": central_rows,
        "worked_example_replacement_pct": worked["replacement_pct"],
        "worked_example_net_inr_per_t": worked["net_inr_per_t"],
        "supply_scaled_gross_credit": supply,
        "sensitivities_at_strength_pass": sensitivities,
    }
    (OUT / "results.json").write_text(json.dumps(results, indent=2), encoding="utf-8")
    pd.DataFrame(central_rows).to_csv(OUT / "benefit_by_replacement.csv", index=False)
    pd.DataFrame(sensitivities).to_csv(OUT / "benefit_sensitivity.csv", index=False)
    plot_ratios(day28, OUT / "strength_ratio_28d.png")

    print(json.dumps({
        "compressive_rows": results["n_compressive_rows"],
        "leave_one_study_out": held_out,
        "agreement": agreement,
        "worked_example_replacement_pct": worked["replacement_pct"],
        "worked_example_net_inr_per_t": worked["net_inr_per_t"],
        "supply": supply,
    }, indent=2))


if __name__ == "__main__":
    main()
