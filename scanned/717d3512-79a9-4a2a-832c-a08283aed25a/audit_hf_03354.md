# [M] GLOBAL-10 | Double Fee May Make A Position Liquidatable

## Summary
Severity: Medium
Contest weight: 0.0954
Dataset id: 18205
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
When increasing or decreasing a position, fees are calculated based on the size of the order and then taken out of the collateral. However, when validating the position with validatePosition and checking isPositionLiquidatable, fees are calculated and applied a second time. This further reduces how much collateral the position has during this validation. This can prevent increasing or decreasing a position as the isPositionLiquidatable check would fail unexpectedly.

## Proof of Concept
https://github.com/GuardianAudits/GMX_3/blob/main/test/Guardian/PoCs/GLOBAL_10.ts

## Recommendation
Check if the position is liquidatable prior to fees being paid and taken out of the collateral.
