# [H] H-01 | Compounding Rewards Dilutes Rewards For Others

## Summary
Severity: High
Contest weight: 0.2224
Dataset id: 20720
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In the rewards system, rewards are not locked and can be claimed at any point in time, even if the user's staking tokens are locked for the 13 week period.
A user with a large portion of the totalSupply may continuously claim their rewards and lock those tokens to gain an even greater portion, whether it be directly staking if the reward token matches the staking token, or with a swap to the staking token from the reward token.
This will ultimately dilute the rewards for other users in the reward period while massively swaying the rewards towards themselves.
The change in distribution is at the expense of other staked users, as there is a set amount to be distributed and the final rewards are dramatically skewed towards the user due to their continuous compounding while other staked users have their rewards fractionalized.

## Recommendation
Consider if this is the expected behavior. If this is expected then clearly document it for users so they have a chance to collect an appropriate amount of rewards. If this is not expected, consider requiring that rewards can only be claimed at the end of the lock period.
