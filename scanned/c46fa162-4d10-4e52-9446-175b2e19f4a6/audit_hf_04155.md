# [M] M-01 | Potential System DoS

## Summary
Severity: Medium
Contest weight: 0.1034
Dataset id: 20721
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In the _updateRewards function the rewardTokens are iterated over to _updateRewardsGlobal for each token. However there is no explicit bound on the length of the rewardTokens array.
As a result it is possible for the rewardTokens array to become so long that updating the rewards for each token requires more gas than the block gas limit allows.
In such a scenario the _updateRewards function and all functions relying on it would be DoS’d.
Similarly in the _getRewards function all rewardTokens are iterated over to pay the user’s rewards.
Therefore the owner may DoS the claiming of rewards by adding many rewardTokens with the addReward function.

## Recommendation
Consider adding a limit to the amount of rewardTokens that may be supported in the addReward function.
