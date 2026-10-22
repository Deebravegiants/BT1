# [H] blacklisted users can claim withdrawn assets after the cooldown period

## Summary
Severity: High
Contest weight: 0.0000
Dataset id: 23364
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
StakingVault::_update uses modifiers notBlacklisted(from) notBlacklisted(to) to prevent blacklisted users from performing most actions.  
But StakingVault::claimWithdraw does not use the notBlacklisted modifier. Hence a user who has been blacklisted after they first withdrew/redeemed can still claim those assets once the cooldown period has expired.

## Recommendation
StakingVault::claimWithdraw should have at least notBlacklisted(msg.sender) and possibly also notBlacklisted(receiver), though the second one is less effective since the user can input an arbitrary address.
