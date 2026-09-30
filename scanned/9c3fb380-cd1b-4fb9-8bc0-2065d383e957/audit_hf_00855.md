# [M] M-15 | Users Lose Their Rewards Upon Liquidation

## Summary
Severity: Medium
Contest weight: 0.0810
Dataset id: 2592
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
During the liquidation of an account, or a vault liquidation users lose their current vested, but unclaimed, RewardDistributor rewards as these amounts are based upon the shares of the current vault epoch. Additionally, as the claimRewards function relies on the vault.currentEpoch() to measure the shares, reward amounts may be perturbed as the vault is liquidated and completely new shares are issued.

## Recommendation
Consider claiming a user’s rewards for their account on an individual liquidation. For vault liquidations, consider using the epoch in which the reward was applicable to measure the rewards earned, this way accounts can still claim their rewards which were attributed for that previous epoch.
