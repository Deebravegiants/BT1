# [M] ORDM-7 | User Can Decrease Position Below Minimum Collateral

## Summary
Severity: Medium
Contest weight: 0.1066
Dataset id: 20554
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In createNewPosition there is a check that prevents an order from being created if the collateral is below a set minimum. This is in part to ensure that liquidations are profitable. However, a user can decrease the position so that the collateral is below the minimum, making liquidations not profitable. In addition, normal users can unintentionally decrease the position to such a low level that they don't bother to close it. Because the position is not being closed and may end up being unprofitable to liquidate, these small positions will reduce the available OI until the keepers opt to liquidate the position which at that point they will be liquidating at a loss.

## Recommendation
Add a minimum collateral check in modifyPosition to ensure the collateral remains above a desired minimum.
