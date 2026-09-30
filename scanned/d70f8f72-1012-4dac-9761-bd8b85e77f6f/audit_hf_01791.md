# [H] MJR-1 Losses are not taken into account in the strategy

## Summary
Severity: High
Contest weight: 0.0346
Dataset id: 9881
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The withdrawer from vault should incur the losses from liquidation caused by his own withdrawal. However, the Strategy.sol#L307 is ignoring possible trove liquidation. Currently liquidation will cause revert, but even if not, currently strategy is ignoring the case of trove liquidation. This may lead to improper accounting of user balances and possible locking of vault withdrawals.

## Recommendation
It is recommended to rewrite logic of liquidatePosition() considering the liquidation.
