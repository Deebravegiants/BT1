# [M] M-22 | USDC Blacklist Prevents Transfers

## Summary
Severity: Medium
Contest weight: 0.0939
Dataset id: 22192
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
When the staking pool token is transferred it will call _setShares(), which will lead to _distributeReward() being called. Inside of _distributeReward(), it will loop through the reward tokens and transfer any rewards to the users. If a user becomes blacklisted from using USDC, _distributeReward() will revert. This, in turn, will lead to the tokens being stuck in the users wallet and become untransferable. Additionally, this prevents a user from calling claimRewards(). They will not be able to claim any other rewards tokens earned outside of USDC.

## Recommendation
Instead of pushing rewards to users automatically, rely on them claiming the rewards themselves and allow them to specify which token they would like to claim.
