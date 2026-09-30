# [M] Incorrect Parameter Ordering in Curve Evaluation

## Summary
Severity: Medium
Contest weight: 0.2735
Dataset id: 5202
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In the EulerSwap swap logic, the call to CurveLib.f is made with an incorrect ordering of parameters during the evaluation of the post-swap state. The function f() is defined to compute a new reserve value based on the curve. However, the EulerSwap contract incorrectly inverts the order of px and py in some branches of its logic:
- yNew = CurveLib.f(xNew, py, px, y0, x0, cx);
+ yNew = CurveLib.f(xNew, px, py, x0, y0, cx);
This misordering distorts the price weight applied in the curve’s internal calculations, leading to incorrect reserve updates and swap results that violate the intended AMM curve. Specifically, this causes inconsistencies in the swap symmetry: when executing an exact-out swap followed by an exact-in reversal using the same token pair and path, the system fails to return to the original state — demonstrating loss or unintended gain.
This error was clearly observed in simulated outputs. For instance, under the following parameter set:
priceX = 1
priceY = 2
x0 = 1000
y0 = 1000
cX = 0.8
cY = 0.8
reserve0 = 1000
reserve1 = 1000
amount = 500
asset0IsInput = False
exactIn = False
The uncorrected logic produced:
Starting reserves: (1000, 1000)
New Reserve: (500.00, 2200.00)
Output: 1200.00
Attempting to reverse this swap using exact input 1200 with exactIn = True should have brought the reserves back to (1000,1000). Instead, the incorrect computation yielded:
New Reserve: (106.11, 2200.00)
Output: 893.89
This asymmetry stems from misaligned price parameters in the curve formula. After correcting the line the outputs aligned as expected. The output of the exact-out leg becomes:
New Reserve: (500.00, 1300.50)
Output: 300.50
and the exact-in reversal with amount = 300 restores the reserves to:
New Reserve: (500.00, 1300.00)
Output: 500.00
This confirms that the pricing logic and reserve transitions now obey the intended curve dynamics and yield symmetry across swap paths.
Visual validation using the provided plot script (see below) further illustrates the discrepancy. The invalid version of the logic plots a destination point far outside the feasible curve region:
Whereas the corrected computation yields a valid, curve-consistent transition:

## Recommendation
All calls to CurveLib.f() and CurveLib.fInverse() must be carefully reviewed to ensure that parameters are passed in the correct order, specifically:
- yNew = CurveLib.f(xNew, py, px, y0, x0, cx);
+ yNew = CurveLib.f(xNew, px, py, x0, y0, cx);
In particular, care must be taken when switching between x-based and y-based flows to ensure that price tokens and reserve coordinates are not accidentally flipped. Consider isolating the curve application logic into well-named wrapper functions that enforce correct parameter order depending on swap direction, reducing the surface area for future human error.
Further, add test cases and simulation plots that validate the invertibility of swaps under various exact-in/exact-out scenarios across curve segments. Plotting the reserve trajectory with respect to the invariant is highly recommended for debugging and internal QA.
