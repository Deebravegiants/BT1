# [M] GMXO-3 | Liquidator Can Force Liquidation

## Summary
Severity: Medium
Contest weight: 0.0901
Dataset id: 20534
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
When calculating the price of GM, the value is adjusted down by any negative price impact upon
withdrawal. A liquidator can shift the price down on a position that is near liquidation by putting
capital into GMX. This will alter the price that is calculated, and put the user in a liquidatable state.
A liquidator can use this to have ﬁrst access to liquidating the user and get a unfair advantage
compared to the other liquidators. Note that this manipulation can be done by non-liquidators as well
to grief other users.

## Recommendation
Document the behavior of GM’s pricing to users and carefully monitor the pricing for manipulation.
Furthermore, utilize higher liquidity pools to minimize price impact.
