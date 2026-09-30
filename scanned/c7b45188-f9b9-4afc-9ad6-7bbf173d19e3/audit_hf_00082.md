# [M] M-22 | Depositors Banned From Rebalancer If Liquidated

## Summary
Severity: Medium
Contest weight: 0.1018
Dataset id: 158
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
A rebalancer position is created when liquidations create an imbalance in the protocol. Although the rebalancer position liquidation price is low (it's configured to have max 3x leverage), there could be cases when this position might get liquidated.
If there are no new depositors or the imbalance is not big enough, this liquidation will not open a new rebalancer position. Users that were participating in the rebalancer position that got liquidated will now be temporarily banned from depositing into the rebalancer again.
This is due to the fact that the user's entryPositionVersion is greater than the _lastLiquidatedVersion.

## Recommendation
If the rebalancer is liquidated, notify the rebalancer contract by executing updatePosition before any early return.
