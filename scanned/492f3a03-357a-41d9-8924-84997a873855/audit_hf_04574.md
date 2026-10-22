# [C] C-05 | Accounting Error In totalAvailableAssetsForVault

## Summary
Severity: Critical
Contest weight: 0.2696
Dataset id: 22177
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
totalAvailableAssetsForVault should return the available assets that a FraxlendPair vault can pull from LendingAsssetVault. However, several accounting errors exist resulting in the under-calculation of available assets. Consider these two examples of a single whitelisted vault with 100% allocation: LendingAssetVault has 10 DAI of which 6 DAI has been withdrawn into FraxPair Vault Example 1 • totalAvailableAssetsForVault will return 0 when it should return 4 instead Example 2 • LendingAssetVault has 10 DAI of which 4 DAI has been withdrawn into FraxPair Vault • totalAvailableAssetsForVault will return (10 - 4) - 4 = 2 when it should return 6 instead As FraxLendPair relies heavily on this function to obtain available assets from LendingAssetVault this results in: 1) preventing further whitelistWithdraw after 50% of assets are withdrawn, 2) inflating utilization rate in FraxlendPair and increase interest charged to borrowers, 3) deposits allowed above the depositLimit.

## Recommendation
Update the function to: uint256 _overallAvailable = totalAvailableAssets(); uint256 _vaultMax = ((_totalAssets * _vaultMaxPerc[_vault]) / PERCENTAGE_PRECISION); uint256 _totalVaultAvailable = _vaultMax > vaultUtilization[_vault] ? _vaultMax - vaultUtilization[_vault] : 0; _totalVaultAvailable = _overallAvailable < _totalVaultAvailable ? _overallAvailable : _totalVaultAvailable; return _totalVaultAvailable;
