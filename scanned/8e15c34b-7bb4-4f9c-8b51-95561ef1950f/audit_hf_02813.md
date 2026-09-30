# [M] Admin can't increase claim balance when hasAllowanceMechanism has been set in Claim contract

## Summary
Severity: Medium
Contest weight: 0.0609
Dataset id: 15537
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
When users creates DAO they specify the claimBalance and later they can increase it. The issue is that when hasAllowanceMechanism is set there's no way to increase claimBalance because depositTokens() won't allow it. This would cause constant claimBalance that admin set during the DAO creation and it won't be possible to increase airdrop total amount.

## Recommendation
Allow admins to increase claimBalance when hasAllowanceMechanism is set.
