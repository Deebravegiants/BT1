# [C] C-07 | Inflation Attack In LendingAssetVault

## Summary
Severity: Critical
Contest weight: 0.2028
Dataset id: 22179
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
https://blog.openzeppelin.com/a-novel-defense-against-erc4626-inflation-attacks The classic inflation attack during the first deposit is possible in the LendingAssetVault (LAV) through the donate function. Attack scenario: • LAV is created. attacker deposits 1 wei of assets and receives 1 share • Attacker observes User depositing 100e18 of assets and frontruns with a donation of 100e18 assets • User deposits 100e18 but receives 0 shares due to rounding down • Attacker redeems 1 share and receives all assets in the vault (200e18 + 1 wei) • User loses all deposits

## Proof of Concept
https://github.com/GuardianAudits/peapods-1/pull/11/files#diff-c1c46c887a4747bb71075f68a0cd08a6c92a0fa12d5a9d851d34aabbaca555bc

## Recommendation
Consider removing the donate function. Or else, consider other forms of protection against inflation attack, see https://blog.openzeppelin.com/a-novel-defense-against-erc4626-inflation-attacks
