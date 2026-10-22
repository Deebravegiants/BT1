# [M] M-13 | Partial Liquidators Not Fairly Rewarded

## Summary
Severity: Medium
Contest weight: 0.1288
Dataset id: 22096
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Keepers that perform partial liquidations on flagged accounts may be responsible for liquidating
multiple open positions.
However, they only receive a static liquidateKeeperCost, as opposed to flagKeeperCost (received by
keeper that flags the account) which increases based on the number of open positions.
If the gas cost of liquidating multiple positions is greater than the reward, these partial liquidation
keepers may not be incentivized to perform the liquidations at all which is detrimental to the system.
On the other hand, the keeper that flags the account for liquidation receives flagKeeperCost
regardless of number of positions that were actually liquidated.
If the liquidation window happened to be small and only one out of many positions were liquidated,
the keeper still receives the cost of liquidating all open positions.

## Recommendation
Consider limiting the flagKeeperCost and increasing liquidateKeeperCost based on the number of
open positions actually liquidated.
