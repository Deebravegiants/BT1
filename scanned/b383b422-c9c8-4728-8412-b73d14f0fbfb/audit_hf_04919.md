# [M] Users can setup hooks to control the expann-

## Summary
Severity: Medium
Contest weight: 0.0563
Dataset id: 22844
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Reentrancy allows to not claim rewards and update tiers. The fix for the issue still allows user's claim the rewards. But as mitigation, the contract will revert. But this still allows the user's to specifically revert on just the last canary tiers in order to always prevent the expansion of the tiers. User's have control over the expansion of tiers.

## Recommendation
No recommendation available
