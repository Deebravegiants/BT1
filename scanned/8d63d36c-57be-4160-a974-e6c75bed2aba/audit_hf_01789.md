# [M] Incorrect implementation of supplyRate()

## Summary
Severity: Medium
Contest weight: 0.0864
Dataset id: 9812
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The supplyRate() function in interest.lua calculates the supply rate based on the current borrow and utilization rates. However, the implementation is incorrect and has two issues: 1. At interest.lua#L54, borrowRateFloat is calculated as borrowRate / rateMul and, therefore, does not need to be divided by rateMul again at interest.lua#L60. 2. At interest.lua#L61, the utilization rate is incorrectly calculated as TotalBorrows / TotalSupply / 10 ^ CollateralDenomination. It should be TotalBorrows / (TotalBorrows + Cash) by definition.

## Recommendation
Consider modifying the supplyRate() function as suggested above.
