# [M] M-16 | Missing Access Control In payDebt

## Summary
Severity: Medium
Contest weight: 0.0919
Dataset id: 22099
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Except for the payDebt function, all other external, state-modifying functions in the Perps-V3 system
have the access control: FeatureFlag.ensureAccessToFeature(Flags.PERPS_SYSTEM).
This could lead to unexpected behavior in the event that the system is paused through the removal
of access to flag feature.
Also, the payDebt function also does not check that the msg.sender is indeed the account owner,
allowing anyone to reduce debt and increase collateral for another account. It is unclear if this is
intended behavior.

## Recommendation
Consider adding to the payDebt function:
FeatureFlag.ensureAccessToFeature(Flags.PERPS_SYSTEM) and
Account.loadAccountAndValidatePermission(accountId,
AccountRBAC._PERPS_MODIFY_COLLATERAL_PERMISSION)
