# [M] M-14 | DOS Of Borrow & Redeem

## Summary
Severity: Medium
Contest weight: 0.1096
Dataset id: 22220
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Each time borrow or redeem is called in FraxlendPairCore, if there are insufficient local assets, then _depositFromVault is called to pull assets from the vault. However, in _depositFromVault there is a check: if (depositLimit < _totalAsset.totalAmount(address(externalAssetVault))) revert ExceedsDepositLimit(); This check prevents the deposit from vault if the vault's allocated assets to the FraxlendPair exceeds the deposit limit. Consider this example:
• FraxlendPair has a deposit limit of 10 ETH
• Vault has 30 ETH and allocates 50% to FraxlendPair
• Borrow/redeem actions cannot go through as the depositLimit check would always fail

## Recommendation
Consider removing the depositLimit check from _depositFromVault. Instead, in LendingAssetVault, apart from percentage based allocations to a FraxLendPair vault, consider checking for the vault's depositLimit too to avoid over-allocation.
