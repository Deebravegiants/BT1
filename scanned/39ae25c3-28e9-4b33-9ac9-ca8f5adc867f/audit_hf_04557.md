# [H] H-03 | Staking Pool Rewards Sniping Is Possible

## Summary
Severity: High
Contest weight: 0.0989
Dataset id: 22160
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
As there is no penalty nor timelock for unstaking with the StakingPoolToken, a user may claim rewards without actually staking by front-running depositReward and do: stake -> depositRewards -> unstake. The user would immediately be eligible to claim rewards at the expense of other users who are staked.

## Recommendation
Consider implementing a timelock or penalty for unstaking. Also, consider using time-weighted reward distribution.
