# [H] feesAccrued or staker principal may be sent as rewards if rewardRate and emissionEnd are not properly calculated

## Summary
Severity: High
Contest weight: 0.1188
Dataset id: 10461
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
As emissionEnd and rewardRate can be freely set (although rewardRate only in the constructor), if emissionEnd x rewardRate is bigger than the amount of tokens sent to the staking contract, stakers may withdraw feesAccrued or other stakers' principal as rewards.

## Recommendation
Limit the rewards to claim to IERC20(basicToken).balanceOf(address(this)) - totalStaked - feesAccrued. To simplify the logic, it might be easier to only unstake in function completeUnstake(), but leave the rewards stored in stakers[msg.sender].reward to be claimed by calling claimReward(). In claimReward(), instead of deleting staker.rewards, set it to staker.rewards = staker.rewards - actuallyWithdrawnRewards.
