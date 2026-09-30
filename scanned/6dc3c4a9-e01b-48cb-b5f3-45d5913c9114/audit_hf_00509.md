# [M] M-01 | Position With Zero Collateral

## Summary
Severity: Medium
Contest weight: 0.0971
Dataset id: 1967
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
When a position is operating with small amounts, the required collateral for the position can be calculated to be zero due to rounding when calculating value of debt. Consequently, a user can modify their position to a size within a couple thousand wei and have to provide zero collateral. All their prior deposited collateral would be returned, and their position would have no backing. In the original review, this issue was not possible since the minimum requiredCollateral was always at least 2 wei.

## Proof of Concept
https://github.com/GuardianAudits/foil-fuzzing/commit/defacd8f629985c2c446dd481b5a078be7990f68

## Recommendation
Have a minimum required collateral.
