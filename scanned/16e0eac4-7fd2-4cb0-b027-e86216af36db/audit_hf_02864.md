# [C] TradableStaking: rewards accounting is corrupted

## Summary
Severity: Critical
Contest weight: 0.1877
Dataset id: 16118
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The TradableStaking contract uses the previousRewardPerToken mapping to keep track of the rewards-per-token, the last time each user updated their rewards. The problem is that this mapping isn't initialized whenever a staking position is created. This means that the first time a user claims rewards, the value of previousRewardPerToken[user] will be zero, so they will receive rewards as if they were the first user to stake their tokens in the contract.
This results in users getting way more rewards than they are entitled to, and the whole system to keep track of rewards will not work.

## Recommendation
Initialize the previousRewardPerToken mapping to the current cumulativeRewardPerTokenStored whenever a staking position is created (this also requires updating cumulativeRewardPerTokenStored). The mapping previousRewardPerToken can also be removed and this field could be added to the Stake struct, as suggested in issue L-05. The logic for deposits, withdrawals and rewards should also be heavily tested.
