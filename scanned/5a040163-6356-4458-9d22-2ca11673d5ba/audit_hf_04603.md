# [M] M-36 | redeemFromVault DOS

## Summary
Severity: Medium
Contest weight: 0.0628
Dataset id: 22208
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
When LAV.redeemFromVault() is called, FraxlendPair.redeem() is called and the returned value (the assets received) are subtracted from the vaultUtilization. Since vaultUtilization is adjusted by dividing in _updateAssetMetadataFromVault, vaultUtilization may end up being 1 wei less than the received assets. Because of this the redeemFromVault transaction will fail.

## Recommendation
Subtract the minimum between the received assets and vaultUtilization.
