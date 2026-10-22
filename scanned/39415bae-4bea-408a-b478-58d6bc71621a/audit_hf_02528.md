# [M] Centralization Risk in Multiple Places

## Summary
Severity: Medium
Contest weight: 0.0697
Dataset id: 13523
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
For `setEmissionLogic` and `setMaterialObject` in `PhiDaily.sol`, it’s documented that `emissionLogic` and `materialObject` should be contracts but in reality, the admin can set any address. With `setTreasuryAddress`, `setMaxClaimed`, `setRoyalityFee` and `setSecondaryRoyalityFee` in `BaseObject.sol` owner can set not validated values which can result in loss of funds for users.

## Recommendation
Add proper address validation and upper-bound checks for the fees setter functions despite the fact all these functions are callable only by the owner.
