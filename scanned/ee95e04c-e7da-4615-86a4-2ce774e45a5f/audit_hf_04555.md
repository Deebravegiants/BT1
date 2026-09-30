# [H] H-01 | Lack Of Access Control In redeemFromVault

## Summary
Severity: High
Contest weight: 0.0942
Dataset id: 22158
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The function redeemFromVault can be called by an attacker who passes in an arbitrary _vault and _amountShares. As this function can be called by anyone, a griefing attack is possible to call redeemFromVault to deny LendingAssetVault of yield (whenever there is available liquidity in FraxlendPair).

## Recommendation
Validate the input data and consider only allowing owner to call redeemFromVault.
