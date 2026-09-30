# [M] M-18 | MAX_COLLATERALS_PER_POSITION_ACCOUNT Can Be Bypassed

## Summary
Severity: Medium
Contest weight: 0.0708
Dataset id: 2119
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
When closing a position, collaterals are added to the user's account, without validation. If a user only partially closes their account, they will then have all of these collaterals as active. When going to deposit collateral, the validation inside of _depositToAccount() will see that the collateral is already active and not revert even though the user is using more collateral assets than allowed.

## Recommendation
If a user is not fully closing their position, validate that they are not exceeding the MAX_COLLATERALS_PER_POSITION_ACCOUNT.
