# [M] ORDM-1 | Execution Fee Could Exceed Collateral

## Summary
Severity: Medium
Contest weight: 0.1266
Dataset id: 20565
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The execution fee is charged whenever a position is modified from the existing position's collateral (excluding the creation of a new position). This poses potential problems as the execution fee could exceed the collateral a position has. Consider a user who wants to close their position because they are getting too close to the liquidation threshold, but now have to firstly increase the collateral of their position just to close their position. In both the increase and the close the user would be charged an execution fee. This is even further problematic because the _increasePosition function will try to deduct the execution fee from the existing collateral, rather than the collateral after it has been increased by userOrder.deltaCollateral. Consequently, the user is stuck until they are liquidated.

## Recommendation
Charge the execution fee after the collateral is increased. Furthermore, consider restricting the execution fee to be less than the market.minCollateral.
