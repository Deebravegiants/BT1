# [M] M-3 TwoWayLendingFactory.createfrompool does not work

## Summary
Severity: Medium
Contest weight: 0.0555
Dataset id: 7117
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
• TwoWayLendingFactory.vy#L249
The TwoWayLendingFactory.createfrompool method always returns an error with CryptoFromPoolVault. It happens so because vault.borrowed_token() was not initialised at the time of validation:
assert pool.coins(collateralix) == vault.borrowedtoken()
• CryptoFromPoolVault.vy#L37

## Recommendation
We recommend passing an initialised Vault to the CryptoFromPoolVault or moving the check to Factory.
