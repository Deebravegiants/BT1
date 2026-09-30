# [M] Rewards are lost when notifyRewardAmount() is called multiple times before the first staker

## Summary
Severity: Medium
Contest weight: 0.5381
Dataset id: 2998
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In notifyRewardAmount(), if there is currently no deposits in the contract (i.e. totalDeposits == 0), reward is assigned to notifiedRewardAmount:
```solidity
} else {
    notifiedRewardAmount = reward;
}
```
However, if notifyRewardAmount() is called multiple times before the first staker, notifiedRewardAmount will simply be overwritten with the new reward amount. As such, rewards from preceding calls to notifyRewardAmount() will be lost since they are no longer tracked.

## Recommendation
Add reward to notifiedRewardAmount instead:
```solidity
notifiedRewardAmount += reward;
```
