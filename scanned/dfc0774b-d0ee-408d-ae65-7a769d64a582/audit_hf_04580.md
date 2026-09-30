# [C] C-11 | Incorrect addInterest Interface

## Summary
Severity: Critical
Contest weight: 0.1037
Dataset id: 22183
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In the function _updateInterestAndMdInAllVaults, which is called during every deposit/mint, addInterest() is called to trigger interest accrual on the FraxlendPair vault. However, the wrong interface is used which should pass bool _returnAccounting as a function input. Therefore, the current implementation would always fail and DOS all deposits into LendingAssetVault.

## Recommendation
Use the correct interface for addInterest.
