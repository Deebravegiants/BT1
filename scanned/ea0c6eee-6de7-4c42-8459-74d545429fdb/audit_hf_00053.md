# [M] ORDA-4 | minOut Applies To Terminal Orders

## Summary
Severity: Medium
Contest weight: 0.0885
Dataset id: 129
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In the orderValueInCollateral function the minOut and minOutLong values are considered regardless of if the order is pending or if it has reached a terminal status. A deposit may have been cancelled or a withdrawal may have been executed, and therefore the Order contract has a distinct amount of short tokens, however the collateral value is still based on the minimum output that was configured for the order. This directly discounts a user’s collateral as they will often receive more than the configured minimum amount.

## Recommendation
If the order has reached a terminal status, return the balance of short tokens converted to market tokens as the orderValueInCollateral.
