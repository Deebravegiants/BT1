# [M] KEY-1 | Wrong Key For Pool Adjustment

## Summary
Severity: Medium
Contest weight: 0.0650
Dataset id: 18499
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The poolAmountAdjustmentKey function in Keys.sol uses the POOL_AMOUNT key instead of the
POOL_AMOUNT_ADJUSTMENT key.
There are luckily no catastrophic consequences as this is an int value and the poolAmountKey is a
uint, however, it poses a significant risk to any future changes and would cause confusion/potential
issues for those reading using the POOL_AMOUNT_ADJUSTMENT key.

## Recommendation
Alter the poolAmountAdjustmentKey function to use the POOL_AMOUNT_ADJUSTMENT key.
