# [M] M-03 | Precision Loss Leads To Reverts In TokenRewards

## Summary
Severity: Medium
Contest weight: 0.0962
Dataset id: 22174
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
When a user receives shares from TokenRewards for the first time, _cumulativeRewards is called to update the user's rewards mapping with an excluded amount. This amount will be used to calculated the user's share of future rewards. The issue occurs in _cumulativeRewards: (_share * _rewardsPerShare[_token]) / PRECISION By rounding down the calculation, it is essentially excludes the user from 1 wei less of rewards, implying the user earned 1 wei more rewards. This will overtime lead to insufficient balance of rewards to transfer out, and DOS all functionality of the contract when that happens.

## Recommendation
Always round up the calculation in _cumulativeRewards when calculating the excluded amount.
