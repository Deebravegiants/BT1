# [M] M-14 | Endorsed Keeper May Receive Excessive Fees

## Summary
Severity: Medium
Contest weight: 0.1014
Dataset id: 21114
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In validateLiquidation, liqKeeperFee is calculated based on liqSize which is expected not to exceed maxLiquidatableCapacity. Therefore, getLiquidationKeeperFee is expected to calculate iterations = 1 and return liquidationFeeInUsd * 1. However, when an endorsed keeper performs a liquidation, liqSize may exceed maxLiquidatableCapacity. In this case, iterations could exceed 1, and the keeper will receive multiples of the keeperFee despite only performing one liquidation. For example, if liqSize = 10 but maxLiquidatableCapacity = 2, then the keeper will receive five times the keeperFee.

## Recommendation
Consider whether this is desired behavior. If it is not desired, then consider adding to getLiquidationKeeperFee: if (ERC2771Context._msgSender() == globalConfig.keeperLiquidationEndorsed) { iterations = 1; }
