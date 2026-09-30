# [M] M-04 | Interest Not Accumulated Before Admin Changes

## Summary
Severity: Medium
Contest weight: 0.0998
Dataset id: 2159
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Interest should always be accrued before updating parameters that will impact the outcome of the next update to fairly calculate the accumulated interest. The _setAdjustSpeed function in the BSetter contract for example can update the adjustSpeed variable that will influence the borrowRate, but it does not accrue interest before updating this variable. Therefore the next time the borrowRate is updated it applies the updated adjustSpeed value on the whole timeElapsed since the last update while in reality a part of the timeElapsed should be calculated with the old adjustSpeed value to fairly update the borrowRate.

## Recommendation
Accrue interest before updating parameters that will impact the outcome of interest related calculations.
