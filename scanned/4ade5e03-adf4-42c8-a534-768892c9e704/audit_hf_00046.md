# [H] LP-3 | Users Can Withdraw Reserved Utilized Collateral

## Summary
Severity: High
Contest weight: 0.1265
Dataset id: 122
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The utilized collateral amount is not factored in when users are depositing and withdrawing, additionally, positions may remain open for a significant amount of time after they are expired. Therefore the utilized collateral can surpass the NAV. As a result, the totalAvailableAssets view function will underflow panic revert and the utilizationRatio will exceed 100% and perturb the interest rate calculations.

## Recommendation
Refactor the option settlement logic such that utilized collateral is reduced to 0 at the end of an epoch when withdrawals are executed.
