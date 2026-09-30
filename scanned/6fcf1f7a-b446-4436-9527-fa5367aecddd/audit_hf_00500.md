# [C] C-01 | Collateral Removed On Position Adjustment

## Summary
Severity: Critical
Contest weight: 0.1817
Dataset id: 1958
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Fee collectors can create under-collateralized positions and collateralize them using depositCollateral. However, when calling increaseLiquidityPosition or decreaseLiquidityPosition, the zero collateral requirement for fee collectors causes updateCollateral to mistakenly remove and transfer all collateral back to the fee collector. This allows fee collectors to withdraw collateral after depositing, potentially any loss at the end of the epoch. This is against protocol spec that the fee collector should never be able to back out of provided collateral, even if adjusting positions.

## Recommendation
updateCollateral should not be triggered for fee collectors when modifying a position or position modification should be restricted during the epoch.
