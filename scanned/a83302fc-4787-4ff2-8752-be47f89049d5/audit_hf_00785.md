# [C] C-03 | DoS Pool By Allowing Excess Borrowing

## Summary
Severity: Critical
Contest weight: 0.2064
Dataset id: 2513
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Users can borrow from the Pool only by using the PositionManager. Although users must deposit enough collateral to pass the health check after borrowing, the Pool does not check if the poolId has enough liquidity to support the amount borrowed. Any amount borrowed that exceeds the poolId liquidity, will effectively steal this liquidity from other pools, and total borrows will be greater than total assets. There are multiple impacts with this issue:
• pool redeems are DoS'ed when calculating:
uint256 assetsInPool = pool.totalAssets.assets - pool.totalBorrows.assets
• lenders won't be able to redeem from other pools, as there is not enough assets in balance
• SuperPool maxWithdraw reverts as getLiquidityOf calculation will underflow

## Recommendation
Prevent positions from borrowing more assets than the liquidity of the poolId.
