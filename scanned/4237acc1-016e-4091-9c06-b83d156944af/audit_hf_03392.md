# [M] IPU-1 | Price Impact Double Counted

## Summary
Severity: Medium
Contest weight: 0.0731
Dataset id: 18500
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
When increasing a position, PositionUtils.validatePosition is called after incrementing the OI for the
position increase. However, the validation will re-compute the price impact amount based on this
updated OI.
The resulting cache.priceImpactUsd in isPositionLiquidatable would be inaccurate to the actual price
impact experienced. Therefore some positions may be errantly prevented from being opened with
this validation.

## Recommendation
Validate the position based on the previous OI, therefore accurately representing the OI delta of the
order.
