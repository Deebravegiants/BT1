# [M] M-02 | Trapped MIM Rewards

## Summary
Severity: Medium
Contest weight: 0.1043
Dataset id: 20722
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In the _rewardPerToken function if the totalSupply is 0 the rewardPerTokenStored is not advanced, meaning that rewards are not accrued until a user stakes.
This behavior is fine when a user does stake at some point during the reward period, however in the case that no users stake for an entire reward period, the rewards for that period will not be distributed and will have to be claimed using the recover function.
In the case where MIM is used as a rewardToken, the undistributed rewards will not be recoverable as the stakingToken cannot be recovered. Therefore any MIM rewards that go undistributed will be locked.

## Recommendation
If the totalSupply is 0 before the end of a reward period be sure to stake a trivial amount in order to capture any undistributed MIM rewards before calling the notifyRewardAmount function.
