# [M] M-09 | Tick Liquidation Penalty Cannot Be Reset

## Summary
Severity: Medium
Contest weight: 0.0814
Dataset id: 166
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In the _removeAmountFromPosition function the liquidationPenalty is not reset on the tick data after all positions have been removed.
Additionally, during the initiate open flow, the existing tick's liquidation penalty as the result of getTickLiquidationPenalty(s, data_.posId.tick) is used to re-assign the new liquidation penalty.
Thus even after all positions have been cleared from the tick, the latest configured liquidation penalty cannot be assigned to this tick.

## Recommendation
Reset the tick's liquidationPenalty to zero after all positions have been removed from the tick in the _removeAmountFromPosition function.
