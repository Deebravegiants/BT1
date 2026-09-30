# [M] DPU-3 | Position Unexpectedly Closed

## Summary
Severity: Medium
Contest weight: 0.0894
Dataset id: 18193
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In the case where a user’s collateral is deemed to be insufficient after removing the initialCollateralDeltaAmount, the initialCollateralDeltaAmount is set to 0. However if the estimatedRemainingCollateralUsd, which was based upon the initialCollateralDeltaAmount being removed from the position’s collateral, is smaller than the MIN_COLLATERAL_USD the position will still be closed. This is unexpected behavior as the initialCollateralDeltaAmount has been set to 0 so the position’s collateral will no longer be less than the MIN_COLLATERAL_USD.

## Recommendation
Do not close the user’s position in the case where the initialCollateralDeltaAmount is set to 0.
