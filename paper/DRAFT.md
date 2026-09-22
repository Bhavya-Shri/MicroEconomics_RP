# Usefulness and recycling benefit of jarosite in concrete: a two-model computational draft

Repository draft for [MicroEconomics_RP](https://github.com/Bhavya-Shri/MicroEconomics_RP). This paper does not list a personal author name because none was supplied for the computational draft. It is not a revision authored by the writers of the civil-engineering review it starts from.

## Abstract

Jarosite is an acidic, metal-bearing residue of zinc smelting. A civil-engineering review treated a reported strength gain at 15% cement replacement as evidence that jarosite should enter concrete, and it described that step as a circular-economy outcome. The review had no dataset, no fitted model, and no account of prices or of leaching as a condition of use. Published mixes also disagree on how large any strength gain is, and on the replacement level at which strength falls back through the control.

This draft rebuilds the question as two linked models, both run from `src/run_models.py`. Model 1 asks whether a mix is useful. The target is the ratio of compressive strength to the control mix in the same study. Inputs are the jarosite replacement of cement and the curing age. A linear model with a squared replacement term, and a random forest, are scored by holding out each study. On that test, errors are about 0.04 to 0.07 in the strength ratio and the coefficient of determination is near zero or negative, so a curve fitted in one laboratory does not predict another. The operational rule is therefore the observations themselves. At 28 days, both open datasets that report a full replacement series stay at or above the control at 5%, 10%, and 15% jarosite, and both fall below the control at 20% and 25%.

Model 2 does not forecast national income. For one tonne of jarosite used in place of one tonne of cement, it adds the retail value of the cement displaced, an optional carbon term, and an optional disposal credit, and it subtracts an optional transport cost. The credit is paid only when the strength rule passes. If lead, cadmium, or silver in a leachate test exceeds the US toxicity-characteristic level, the credit is zero. None of the mixes in the compiled table has a leachate concentration, so every rupee figure below is conditional on a test this dataset does not contain. In that conditional central case, a passing tonne is worth the central retail cement price used here, Rs 8,000. Applied to an illustrative jarosite supply of about 0.41 million tonnes, that is a gross cement-value displacement of about Rs 3.27 billion, not a change in GDP.

## 1. Introduction

India’s primary zinc smelters produced 817,058 tonnes of zinc in 2024, on the U.S. Geological Survey country table (U.S. Geological Survey, n.d.). The earlier review’s figure of about 2.5 lakh tonnes is too small for that year and is not used. Jarosite is the iron-sulphate residue of the roast-leach-electrowin route. Kangas et al. (2017), as cited in that review, put the residue at about half a tonne per tonne of zinc. A separate open paper puts Indian jarosite arisings near 0.25 million tonnes a year (Nandi and Ransinchung, 2021). Another puts Hindustan Zinc’s Chittorgarh arisings near 0.5 million tons a year, with a larger accumulated stock (Sharma, 2021). These supply figures are scenarios, not one audited mass balance. Hindustan Zinc’s FY2023-24 environment report states that 163,795 tonnes of jarosite were used in cement construction, and that a feasibility study with IIT Roorkee considered 10–15% replacement of cement in concrete, mortar, and pavers (Hindustan Zinc, 2024).

The environmental case for doing something other than storage is the metals in the residue. Raw jarosite is described as hazardous, and open papers report that unbound residue can exceed regulatory leaching levels (Nandi and Ransinchung, 2021; Mehra, Gupta and Thomas, 2016). Binding it in cement is one proposed control. The industrial case is the cement that binding can displace. Indian cement-sector emissions were about 0.68 tonnes of CO2 per tonne of cement in 2020, on the path described by the GCCA India roadmap, and cement output is hundreds of millions of tonnes a year (GCCA India, 2025). A few hundred thousand tonnes of jarosite cannot change national cement demand. They can change the disposal account of the zinc industry if each reused tonne actually replaces cement and stays inside leaching limits.

Laboratory papers do not give one strength result. Nandi and Ransinchung (2021) report 28-day paver compressive strength 19.1% above the control at 15% jarosite and 4.9% below the control at 20%. Sharma (2021) reports a smaller 28-day gain, about 6.5% at 10% replacement, and a result below the control from 20% upward. Afaque et al. (2024) report a 56-day compressive strength slightly above the control at 15% and below it at 20%, while split tensile strength in the same programme stays below the control at every jarosite level they give numbers for. The source review’s abstract collapses this spread into one claim, a 17% strength increase at 15% replacement, taken from Gared and Gaur. Their open abstract says strength rose as jarosite rose from 0 to 25% and does not state 17% (Gared and Gaur, 2021). That number is not used in this draft.

Gupta and Sachdeva (2021) already fitted neural networks to compressive and flexural strength inside one M40 pavement programme, with jarosite at 0–25% and six curing ages. This draft does not have those 90 rows. Copying a neural-network architecture onto three published curves would only hide the small sample. The computer-science task is narrower: compile the rows that can be checked, test whether a model fitted on one study predicts another, and price a tonne only when the strength rule and the leaching rule both allow it.

The system boundary is the path from smelter residue to a concrete mix that replaces cement. Red mud, which appears in the source review’s circular-economy section, is outside that boundary. So is any claim about gross domestic product. The objects the models return are a strength ratio, a pass or fail or untested leaching label, and rupees per tonne of jarosite under stated prices.

## 2. Methodology

### 2.1 What was collected

The workspace contained the source review and no other uploaded papers, and the GitHub repository was empty. The dataset is therefore limited to figures that could be read in open papers as either a strength and its control, or a percentage versus that control. Rows are in `data/literature_mixes.csv`. Each row names the study, the product, the component replaced, the replacement percentage, the water–cement ratio when the paper holds it fixed, the curing age, the property, the strength ratio, the leaching status, and the sentence or table the number came from.

Three compressive series are included.

- Sharma (2021), pavement concrete, cement replacement from 0 to 30% in steps of 5, at 7 and 28 days. Table 14 gives the megapascal values. The paper’s mix design discusses a water–cement ratio near 0.38 and then says extra water was added because jarosite raised water demand, so the water–cement ratio is not stored as a constant.
- Nandi and Ransinchung (2021), paver blocks, water-to-cementitious ratio fixed at 0.43, cement replacement from 0 to 25%. Section 3.2.1 states the 7-day and 28-day compressive changes versus the control. The 7-day text states the gains at 5, 10, and 15% only, so 20% and 25% are not filled in. Section 3.2.2 states 28-day flexural gains at 5, 10, 15, and 20%. The 25% flexural result is described as comparable to the control and is left blank rather than coded as zero or as one.
- Afaque et al. (2024), M45 concrete, water–cement ratio 0.40. The 56-day compressive strengths of the control (57.4 MPa), the 15% mix (58.63 MPa), and the 20% mix (54.04 MPa) are paired. The 28-day and 56-day split tensile pairs are included as a separate property. A 10% compressive strength is mentioned in a damaged passage of the open text without a clear age, and it is omitted.

The 17.88% figure, the source review’s leaching table, and any strength read off a graph are omitted. The leaching table’s columns did not survive the Word conversion in an alignment that could be checked against the papers.

The compiled file has 40 rows. Twenty-seven are compressive. Every row has leaching status `untested`.

### 2.2 Model 1: usefulness

The target is the strength ratio

\[
R = \frac{f}{f_{\text{control}}}
\]

with \(f\) and \(f_{\text{control}}\) measured in the same study, at the same age, on the same property. A ratio of 1 means the jarosite mix matched the control. Using the ratio, rather than megapascals, is what makes a pavement concrete, a paver, and an M45 mix comparable. Absolute strength is still stored when the paper printed it.

The compressive model uses three inputs: replacement percentage \(x\), \(x^2\), and curing age in days. The squared term is there because the published series rise and then fall. Water–cement ratio is not a model input. It is constant inside Nandi and Ransinchung and inside Afaque et al., and it is not a reliable constant in Sharma, so it would act as a study label rather than as a mix variable.

Two estimators are fit with scikit-learn. The first is ordinary linear regression on \(x\), \(x^2\), and age. The second is a random forest of 200 trees, depth at most 3, at least two samples in a leaf, random seed 0. There is no neural network. Gupta and Sachdeva had 90 observations from one lab. This file has 27 compressive rows from three labs.

Validation is leave-one-study-out. Each study is predicted only by the other studies. Mean absolute error, root mean squared error, and \(R^2\) are reported on the held-out study. A negative \(R^2\) means the predictions are worse than guessing the held-out mean. That comparison is the one that matters here, because the scientific claim in the source review is that one replacement level can be carried from paper to paper.

A separate quadratic is fit inside each 28-day series,

\[
R = a + bx + cx^2,
\]

only as a smooth description of that series. It is not the rule that releases the economic credit. On the Nandi series the quadratic still sits above 1 at 20% replacement (fitted ratio about 1.04) where the stated result is 0.951. A smooth curve that erases the failure point is the wrong object to price.

The usefulness rule used downstream is observational:

- At a replacement level tested by both Sharma (2021) and Nandi and Ransinchung (2021) at 28 days, the level passes the strength screen only if both ratios are at least 1.
- A level tested by only one of them is not given a shared pass.
- Flexural and split tensile ratios are reported and do not override a compressive result. In these papers they do not tell the same story as compressive strength. Nandi and Ransinchung still have a 28-day flexural ratio of 1.02 at 20% jarosite, where compressive strength has already fallen below the control. Afaque et al. report 28-day split tensile ratios of about 0.80, 0.95, and 0.92 at 10, 15, and 20%.

### 2.3 Leaching screen

A mix is not cleared for use by strength alone. The screen looks only at metals with a US toxicity-characteristic level: lead 5 mg/L, cadmium 1 mg/L, and silver 5 mg/L (the levels used as the regulatory comparison in this draft). Zinc, copper, and iron are not assigned a limit. The source review’s limit row included those three metals; they are not on the toxicity-characteristic list, and inventing a cutoff would repeat the problem.

For a sample that reports one or more of lead, cadmium, and silver, the status is `fail` if any reported value is above its level, and `pass` if every reported one of those metals is at or below its level. If none of the three is reported, the status is `untested`. An untested mix can still be priced, and the price is labelled conditional. A failed mix receives no recycling credit. The function is in `run_models.py`. The three illustrative calls in that file are checks of the logic, not data, and they are not written into the result tables.

No row in `literature_mixes.csv` reaches `pass` or `fail`. Mehra, Gupta and Thomas (2016) and Ray et al. (2020) report, in abstract, that leaching from their hardened jarosite mixes met the limits they used. Those sentences are prior evidence that a pass is possible. They are not measurements attached to the Sharma, Nandi, or Afaque mixes.

### 2.4 Model 2: benefit per tonne

Model 2 is an account, not a second machine-learning fit. There is no time series of jarosite recycling and no income variable to learn. The unit is one tonne of jarosite that replaces cement, which is the replacement used in all three compressive series. Sand replacement would displace little or no cement and is a different account; it is not in this dataset.

Let \(q\) be the tonnes of cement credited per tonne of jarosite. Under the threshold rule, \(q = 1\) when the strength screen passes and the leaching status is not `fail`, and \(q = 0\) otherwise. A proportional rule, \(q = \min(1, \max(R, 0))\), is implemented and is not the central case, because a mix below the control is not treated here as a partial success.

Net benefit in rupees per tonne is

\[
B = q \cdot P + q \cdot e \cdot C + D - T
\]

when leaching is not `fail`, and \(B = 0\) when it is. \(P\) is the cement price in rupees per tonne, \(e\) is tonnes of CO2 per tonne of cement, \(C\) is a carbon price in rupees per tonne of CO2, \(D\) is an avoided disposal cost, and \(T\) is transport and processing cost.

Central values, stored in `data/parameters.json`:

- \(P = 8000\), from a retail bag price of Rs 400 per 50 kg. The low and high retail scenarios are Rs 7,400 and Rs 8,600 per tonne, from bag prices of about Rs 370 and Rs 430. These are not ex-works prices. A retail valuation overstates the resource cost of cement relative to a factory price.
- \(e = 0.68\) in the central case (GCCA India, 2025, 2020 sector intensity). A high case uses \(e = 0.90\), the order of magnitude cited by Nandi and Ransinchung (2021). Basavaraj and Gettu (2025) report about 0.91–1.00 tonnes CO2e per tonne of OPC on a ground-to-gate basis, which sits next to that high case.
- \(C = 0\), \(D = 0\), and \(T = 0\) in the central case. No single Indian carbon price, hazardous-waste tipping fee, or haul cost was taken from a citable series. Non-zero values appear only as labelled scenarios: carbon at Rs 500 and Rs 2,000 per tonne of CO2; disposal at Rs 1,500 and Rs 4,000 per tonne; transport at Rs 500 and Rs 2,000 per tonne.

Gared and Gaur (2021) say that disposal practice adds 2% lime and 10% cement to make jarofix before the residue is dumped. If that is the counterfactual, one tonne of jarosite diverted from jarofix also avoids 0.10 tonnes of cement. That credit is a switch, off in the central case, because this draft does not observe the disposal route of each tonne. Lime is recorded and not priced.

The 15% level is the worked example. It is the highest replacement at which both 28-day series still pass, so a cubic metre of concrete can take more jarosite there than at 5% or 10% without failing the shared strength rule. The gross figure for a supply scenario is \(B\) times tonnes of jarosite. Four supplies are scaled:

- USGS 2024 primary smelter output times 0.5, which is 408,529 tonnes.
- That quantity minus the 163,795 tonnes Hindustan Zinc reports as already used in cement construction. The subtraction mixes a 2024 national generation factor with a FY2023-24 company use figure. It is an illustration of “not already reported as used”, not a closed balance. The remainder is 244,734 tonnes.
- 250,000 tonnes, the Nandi and Ransinchung citation.
- 500,000 tonnes, the Sharma citation for Hindustan Zinc at Chittorgarh.

Cement production in India was about 334 million tonnes in 2019–20 on the same GCCA roadmap, so a 15% replacement niche in national cement output is far larger than any of these jarosite supplies. Supply, logistics, and the leaching rule are the constraints. Cement demand is not.

### 2.5 What the design can support

The design can show which published replacement levels in the compiled 28-day series are at least as strong as their controls, how badly a model fit on the other studies misses a held-out study, and how many rupees of cement value one passing tonne represents at a stated bag price. It can show that a leaching failure removes that value, and that carbon, disposal, and haul costs move it only inside the scenarios that were typed in.

It cannot support a new cylinder or cube test, a neural-network accuracy claim, a prediction of GDP, or a statement that any mix in the file is safe to use. The last point stands until a leachate concentration for that mix is in the table.

## 3. Results

### 3.1 Strength ratios at 28 days

Figure `outputs/strength_ratio_28d.png` plots the two full 28-day compressive series. The ratios below are strength divided by the study’s own control.

| Jarosite, % of cement | Sharma (2021) | Nandi and Ransinchung (2021) | Both at least 1? |
| --- | ---: | ---: | --- |
| 0 | 1.000 | 1.000 | control |
| 5 | 1.064 | 1.034 | yes |
| 10 | 1.065 | 1.117 | yes |
| 15 | 1.030 | 1.191 | yes |
| 20 | 0.958 | 0.951 | no |
| 25 | 0.932 | 0.956 | no |

Sharma’s 30% mix is 0.889 of the control. That level is absent from Nandi and Ransinchung, so it is not a shared pass. Sharma’s own 28-day peak is 10% (41.40 MPa against a control of 38.86 MPa). Nandi and Ransinchung’s stated peak is 15% (+19.1%). The shared screen still passes at 15% because Sharma remains 3.0% above the control there. The size of the gain is not shared. Treating “15% gives about 17% more strength” as a single fact erases a gain of 3% in one study and 19% in the other.

The within-study quadratics peak at 8% for Sharma (fitted ratio about 1.04) and at 11% for Nandi and Ransinchung (fitted ratio about 1.12). Those peaks are smoother than the data. They are not used to choose the worked example.

Afaque et al. (2024), at 56 days, give compressive ratios of 1.021 at 15% and 0.941 at 20%. That agrees with the pass at 15% and the fail at 20%. It is one more study, two non-control points, and a different age. Their split tensile results stay below the control, so a compressive pass is not a general strength pass.

### 3.2 Does a model fitted elsewhere predict the held-out study?

Leave-one-study-out on the 27 compressive rows:

| Held-out study | Rows | Quadratic linear MAE | Quadratic linear \(R^2\) | Random forest MAE | Random forest \(R^2\) |
| --- | ---: | ---: | ---: | ---: | ---: |
| Afaque et al. (2024) | 3 | 0.042 | −1.02 | 0.042 | −1.97 |
| Nandi and Ransinchung (2021) | 10 | 0.065 | −0.02 | 0.059 | 0.11 |
| Sharma (2021) | 14 | 0.060 | −0.28 | 0.066 | −0.50 |

An MAE of 0.06 is six percentage points on the strength ratio. That is large next to Sharma’s entire 28-day gain, and smaller than Nandi and Ransinchung’s gain at 15%. The negative \(R^2\) values mean the held-out study is not a draw from the same curve. The forest’s only positive \(R^2\) is 0.11, on the Nandi hold-out. Model 1, as a portable predictor, fails the test this sample can actually run. The useful output is the paired observation table, not the fitted function. Adding a deeper network would not create the missing rows.

### 3.3 Benefit, conditional on leaching

At every shared level from 5% through 15%, both studies pass the strength rule, leaching is untested, and the central account sets \(q = 1\), \(C = 0\), \(D = 0\), and \(T = 0\). Then

\[
B = 8000 \text{ rupees per tonne of jarosite}.
\]

At 20% and 25%, \(q = 0\) and \(B = 0\) on the strength rule alone. The worked example is 15%, because that is the highest shared pass and therefore the largest jarosite intake per cubic metre among the shared passes. The rupees per tonne do not rise between 5% and 15%. What rises is how much residue a given volume of concrete can absorb before the strength screen fails.

Scaled by supply, still conditional on leaching compliance, and still a gross retail cement value rather than value added:

| Supply scenario | Tonnes of jarosite | Gross cement credit |
| --- | ---: | ---: |
| 0.5 t residue per t zinc, on 817,058 t primary zinc | 408,529 | Rs 3.268 billion |
| Same, minus 163,795 t reported as already used in cement | 244,734 | Rs 1.958 billion |
| 0.25 million t, Nandi and Ransinchung citation | 250,000 | Rs 2.000 billion |
| 0.5 million t, Sharma citation for one plant | 500,000 | Rs 4.000 billion |

The middle row is the least misleading “additional” figure, and it is still not a mass balance. If the 163,795 tonnes already used are real, a large part of the cement credit may already be occurring. This draft does not know the replacement percentage of that reported use.

Sensitivity around a strength pass, still untested for leaching:

| Case | Net, rupees per tonne |
| --- | ---: |
| Central, cement only | 8,000 |
| Retail cement Rs 7,400 or Rs 8,600 | 7,400 or 8,600 |
| Carbon at Rs 500 / t CO2, \(e = 0.68\) | 8,340 |
| Carbon at Rs 2,000 / t CO2, \(e = 0.68\) | 9,360 |
| Carbon at Rs 2,000 / t CO2, \(e = 0.90\) | 9,800 |
| Assumed disposal credit Rs 1,500 or Rs 4,000 | 9,500 or 12,000 |
| Assumed transport Rs 500 or Rs 2,000 | 7,500 or 6,000 |
| Jarofix switch on (extra 0.10 t cement) | 8,800 |
| Leaching status set to fail | 0 |

At these scenario carbon prices, the cement price dominates the carbon term. A leaching failure dominates both. That is the pollution result in this model: the dataset cannot show a pass, and the account is built so that a fail removes the benefit rather than sitting in a later section of the paper.

## 4. Conclusion

The source review’s circular-economy claim needed a dataset, a rule for conflicting strength results, and a unit in which “benefit” is a number. The compiled open data support a shared 28-day compressive pass at 5, 10, and 15% cement replacement, and a shared fail at 20 and 25%. They do not support a portable regression or forest, and they do not support the single 17% gain. The central recycling benefit is Rs 8,000 of retail cement value per tonne of jarosite that passes the strength rule, or zero if it fails the leaching rule. Every tonne in the present file is still untested on that rule, so the billion-rupee supply totals are conditional upper accounts. They are not an economic forecast.

The next data step is to add leachate concentrations, in mg/L, for lead, cadmium, and silver on the same mixes, and to replace the retail cement price with an ex-works price and a measured disposal and haul cost. Until those rows exist, the code should be re-run rather than edited by hand: `python src/run_models.py`.

## References

Afaque, M., Khan, R.A., Roy, S. and Khan, M. (2024) ‘Mechanical and microstructural analysis of jarosite-enhanced concrete for sustainable construction’, *E3S Web of Conferences*, doi: 10.1051/e3sconf/202459601020.

Basavaraj, A.S. and Gettu, R. (2025) ‘Comparison of critical input parameters and key environmental indicators for cement production in India’, doi: 10.70002/iitm.rdr.1.1.37.

Gared, O. and Gaur, A. (2021) ‘Feasibility study of jarosite as cement replacement in rigid pavement’, *Materials Today: Proceedings*, 44, pp. 4337–4341, doi: 10.1016/j.matpr.2020.10.554.

GCCA India (2025) *Decarbonization roadmap for the Indian cement sector: net-zero CO2 by 2070*, executive summary. Available at: https://gccassociation.org/wp-content/uploads/2025/03/Excutive-summary-Roadmap.pdf (accessed 22 September 2026).

Gupta, T. and Sachdeva, S.N. (2021) ‘Prediction of compressive and flexural strengths of jarosite mixed cement concrete pavements using artificial neural networks’, *Road Materials and Pavement Design*, 22(7), pp. 1521–1542, doi: 10.1080/14680629.2019.1702583.

Hindustan Zinc (2024) *Integrated annual report FY2023-24*, environment section. Available at: https://integratedreport.hzlindia.com/annual-integrated-report-fy-2023-24/environment.php (accessed 22 September 2026).

Kangas, P. et al. (2017) ‘Hydrometallurgical processing of jarosite to value-added products’, *Mineralteknik 2017*. Cited from the source review for the 0.5 t residue per t zinc factor. Not remeasured here.

Mehra, P., Gupta, R.C. and Thomas, B.S. (2016) ‘Properties of concrete containing jarosite as a partial substitute for fine aggregate’, *Journal of Cleaner Production*, 120, pp. 241–248, doi: 10.1016/j.jclepro.2016.01.015.

Nandi, S. and Ransinchung, G.D.R.N. (2021) ‘Utilization of jarosite in precast concrete paver blocks’, *IOP Conference Series: Materials Science and Engineering*, 1075, 012024, doi: 10.1088/1757-899X/1075/1/012024.

Ray, S., Daudi, L., Yadav, H. and Ransinchung, G.D. (2020) ‘Utilization of jarosite waste for the development of sustainable concrete by reducing the cement content’, *Journal of Cleaner Production*, 272, 122546, doi: 10.1016/j.jclepro.2020.122546.

Sharma, P. (2021) ‘Effect of jarosite waste on pavement quality concrete’, *Journal of Emerging Technologies and Innovative Research*, 8(6), JETIR2106715. Available at: https://www.jetir.org/papers/JETIR2106715.pdf (accessed 22 September 2026).

U.S. Geological Survey (n.d.) *India*. National Minerals Information Center. Primary zinc smelter production, 2024: 817,058 t. Available at: https://www.usgs.gov/centers/national-minerals-information-center/india (accessed 22 September 2026).
