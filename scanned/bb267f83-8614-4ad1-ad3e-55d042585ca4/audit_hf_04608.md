# [M] M-41 | Donation Increases Share Supply

## Summary
Severity: Medium
Contest weight: 0.1053
Dataset id: 22213
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Function donate aims to increase the totalAssets of the LendingAssetVault without increasing the totalSupply of shares, hence a donation. The issue is that _burn(address(this), convertToShares(_assetAmt)); converts the _assetAmt to shares after _deposit(_assetAmt, address(this)); already minted shares, so the newly calculated share amount to burn will be less than the calculated and minted shares in _deposit. Ultimately, function donate increases the totalSupply even though it is not meant to.

## Proof of Concept
https://github.com/GuardianAudits/peapods-fuzzing/blob/504c79e9f12f6b586fe627b42dc9ac29df106ddf/test/invariant/helpers/ForgeTester.sol#L129

## Recommendation
Burn the entire added supply post-deposit.
