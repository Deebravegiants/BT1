# [M] M-05 | Inefficient Distribution In StakingRewards

## Summary
Severity: Medium
Contest weight: 0.1058
Dataset id: 2297
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
If stake is not called in the same block of notifyRewardAmount, depending on delay, a portion of
rewards will remain unused inside the contract.
For example, at time X rewards are transferred into the contract. Then some time Y has passed
before the first user stakes. However, the reward period will end at X + rewardsDuration not X + Y +
rewardsDuration.
Therefore, the rewards for Y * rewardRate will remain un-distributed till the next cycle. If a new
reward cycle is never started (e.g. final cycle), then any undistributed amount will remain inside the
contract.

## Proof of Concept
https://github.com/GuardianAudits/truth-markets-1/pull/2/files

## Recommendation
Consider defining periodFinish in the first stake that is done after notifyRewardAmount, when total
deposits are zero.
