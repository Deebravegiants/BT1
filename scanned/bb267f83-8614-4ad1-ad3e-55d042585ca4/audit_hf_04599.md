# [M] M-33 | LendingAssetVault Asset/Share Conversion Error

## Summary
Severity: Medium
Contest weight: 0.0775
Dataset id: 22204
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Similarly to M-20, the LendingAssetVault::withdraw() and LendingAssetVault::mint() perform asset and share conversions with an update to _cbr() taking place in between. This takes place with the call to _updateInterestAndMdInAllVaults() happening in _withdraw() and _deposit(). This will lead to a similar scenario where the accounting for assets will be incorrect for withdrawals and the shares will be incorrect for mints compared to the amounts requested.

## Recommendation
_updateInterestAndMdInAllVaults() should be called in the beginning rather than between conversions.
