# [H] H-01 | Sqrt Price Compared With Price

## Summary
Severity: High
Contest weight: 0.1104
Dataset id: 2019
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In the _getUtilizationRate function the priceAdj is computed as:
FixedPointMathLib.divWad(TickMath.getSqrtRatioAtTick(activeTickAdj), FixedPoint96.Q96);
Which has units of the square root of the price. However the priceAdj is compared against the result
of getBLV to compute the premiumRatio.
The result of getBLV is a price, instead of a square root price. Therefore the premiumRatio is
incorrect.

## Recommendation
Square the priceAdj to compute the correct price.
