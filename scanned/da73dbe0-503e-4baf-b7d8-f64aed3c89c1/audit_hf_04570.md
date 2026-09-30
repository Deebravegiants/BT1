# [M] M-02 | Underflow In _updateAssetMetadataFromVault

## Summary
Severity: Medium
Contest weight: 0.1481
Dataset id: 22173
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Whenever _updateAssetMetadataFromVault is called, a vault's Collateral Backed Ratio (CBR) is updated and compared against its previous value. If the CBR decreased from the previous update, then the vault's utilization is also decreased based on _vaultAssetRatioChange. The issue occurs when _vaultAssetRatioChange is greater than 100%. This leads to an underflow when updating vaultUtilization[_vault]. Consider this example: • Vault's CBR decreased from 100e27 to 49e27 • _vaultAssetRatioChange: (100e27 * 1e27 / 49e27 ) - 1e27 = 1.04e27 • vaultUtilization[_vault]: 100 - (100 * 1.04e27 / 1e27) = underflow Such a drastic drop in CBR is unlikely but possible in vaults with obscure tokens (as Peapods is designed to be used permissionlessly). A revert in the update for one vault will cause DOS in all whitelisted vaults, and prevent liquidations in FraxlendPair vaults.

## Proof of Concept
https://github.com/GuardianAudits/peapods-1/pull/10/commits/336bec48aeb9065f048b9b98631cf8f585d25a3e

## Recommendation
Handle the case when _vaultAssetRatioChange is greater than 100% to avoid the underflow.
