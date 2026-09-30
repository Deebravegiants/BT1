# [M] M-03 | Incorrect deltaCollateral Check When Negative

## Summary
Severity: Medium
Contest weight: 0.1039
Dataset id: 1985
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Users provide deltaCollateralLimit when modifying their trade positions. While a positive deltaCollateralLimit indicates the maximum amount a user wants to provide to the protocol, a negative deltaCollateralLimit represents the minimum collateral amount a user wishes to receive from the protocol when decreasing or closing a position. However, the negative case in _checkDeltaCollateralLimit is incorrect and behaves oppositely. It reverts when deltaCollateralLimit < 0 && deltaCollateral < deltaCollateralLimit. The user-provided value functions as a maximum limit instead of a minimum limit, resulting in the user receiving less than intended all the time.

## Recommendation
Change deltaCollateral < deltaCollateralLimit to deltaCollateral > deltaCollateralLimit.
