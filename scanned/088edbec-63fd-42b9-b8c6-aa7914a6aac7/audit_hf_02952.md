# [M] Undistributed rewards may be stuck in the contract if no stakers exist in a cycle

## Summary
Severity: Medium
Contest weight: 0.0811
Dataset id: 16368
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In the StakingVault contract, rewards are received from the PositionManager via acceptPositionManagerRewards(). These rewards are then distributed equally among pools for the current cycle. However, if no stakers exist in a particular cycle, the rewards for that cycle will remain stuck in the contract, as the undistributed rewards from cycles without stakers are not migrated to the next cycle, unlike cycle shares, which are migrated when a new cycle opens via endCycleIfNeeded().

## Recommendation
VoltStakingReport.md Implement a sweep() function to rescue stuck rewards from cycles with no stakers.
