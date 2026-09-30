# [M] Insufficient input validation

## Summary
Severity: Medium
Contest weight: 0.0880
Dataset id: 15754
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Throughout the codebase there are couple of places where important input validation is missing. The inputs are not constrained at all or only partly.  
The newCloseFactorMantissa param in Comptroller:_setCloseFactor().  
The supplySpeed and borrowSpeed params in CompLogic:_setCompSpeedInternal().  
The _rewardsDuration param in StakingRewardsMultiGauge:setRewardsDuration() is only partly validated but it is missing an upper constrain.  
The new_rate param in StakingRewardsMultiGauge:setRewardRate().  
SumerMoney_report.md

## Recommendation
You can create a check where exampleParam should be less than x or greater than y, otherwise revert the transaction.
