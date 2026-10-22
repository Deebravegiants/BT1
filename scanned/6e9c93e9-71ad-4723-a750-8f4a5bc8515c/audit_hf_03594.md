# [C] LOTY-1 | All Loyalty Rewards Can Be Stolen

## Summary
Severity: Critical
Contest weight: 0.1731
Dataset id: 19573
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The functions supply() and withdraw() call accrueRewards() before mutating the points balance of a user. burnTokens() does not which allows someone to claim an abnormally large portion of the rewards by abusing their rewardsIndex and an artificially high balance of points that did not get accrued when incremented. This allows such a user to burn AMBT just before they withdraw and receive much more rewards than they should. This will also brick the reward claim process for other users as the reward token balance of the contract will not be enough to cover for their rewards.

## Recommendation
Call accrueRewards() before mutating the user's balance2 in burnTokens().
