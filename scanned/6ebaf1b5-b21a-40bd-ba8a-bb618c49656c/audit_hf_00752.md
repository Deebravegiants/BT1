# [H] H-02 | Resolver Might Not Receive The Deserved Reward

## Summary
Severity: High
Contest weight: 0.1704
Dataset id: 2312
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
When a market is finalized and ends with _CANCELED as the winningPosition, users can trigger
withdrawFromCanceledMarket to withdraw their payment tokens.
Within withdrawFromCanceledMarket, if bondSettled is not yet settled, it will trigger _settleBonds to
handle reward payments and bond refunds or slashes.
However, if the market previously entered a dispute or escalation state, it will transfer the reward to
the safeBoxAddress when the winningPosition is _CANCELED, regardless of whether the
originalOutcomeFromResolver is equal to _CANCELED.
This will result in the resolver not receiving the deserved reward.

## Recommendation
Only transfer reward to safeBoxAddress when winningPosition is _CANCELED and winningPosition is
not equal to originalOutcomeFromResolver.
