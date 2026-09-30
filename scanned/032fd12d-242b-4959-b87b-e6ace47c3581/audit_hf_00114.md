# [H] Rewards cannot be withdrawn

## Summary
Severity: High
Contest weight: 0.1603
Dataset id: 235
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The rewards for a recipient in `IncentiveDistribution.sol` are stored in the storage mapping indexed by recipient `accruedReward[recipient]` and the recipient is the actual margin trader account, see `updateAccruedReward`.

These rewards are supposed to be withdrawn through the `withdrawReward` function but `msg.sender` is used here instead of a `recipient` (`withdrawer`) parameter. However, `msg.sender` is enforced to be the incentive reporter and can therefore not be the margin trader.

Nobody can withdraw the rewards.

Recommend removing the `isIncentiveReporter(msg.sender)` check from `withdrawReward` function.

## Recommendation
No recommendation
