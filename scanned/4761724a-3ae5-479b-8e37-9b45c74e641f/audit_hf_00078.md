# [M] M-18 | No Rebalancer Trigger On Individual Liquidation

## Summary
Severity: Medium
Contest weight: 0.1260
Dataset id: 154
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
When closing a position the position has already been removed from the tick cumulatives as well as the exposure and balance of the aggregate long tracking.
When the close action is validated the vault balance is then incremented by the entire position value to account for this position being liquidated.
However since this liquidation logic is separated from the tick cumulative liquidation the rebalancer position will not be triggered when the individual position liquidation would be the one to set the net imbalance over the _closeExpoImbalanceLimitBps.
As a result the liquidation of a single large position upon the validation of its close action could adversely affect the balance of exposures without a counter-action from the rebalancer position.

## Recommendation
Consider if this behavior and corresponding risk of imbalance without counter-action from the rebalancer position is acceptable.
If it is not, consider triggering the rebalancer after the individual position liquidation occurs in the _validateClosePositionWithAction function.
