# [M] vaultUtilization is updated incorrectly

## Summary
Severity: Medium
Contest weight: 0.4265
Dataset id: 11511
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Inside the LendingAssetVault.sol a vault's utilization is updated inside the _updateAssetMetadataFromVault based on how much the CBR changed from the last update. In short, if the cbr decreased then the vault utilization would decrease and increase otherwise. The logic that handles this is (a snippet from the _updateAssetMetadataFromVault):
```solidity
uint256 _vaultAssetRatioChange = _prevVaultCbr > _vaultWhitelistCbr[_vault]
    ? (PRECISION * _prevVaultCbr) / _vaultWhitelistCbr[_vault]) - PRECISION
    : (PRECISION * _vaultWhitelistCbr[_vault]) / _prevVaultCbr) - PRECISION;
uint256 _currentAssetsUtilized = vaultUtilization[_vault];
uint256 _changeUtilizedState = (_currentAssetsUtilized * _vaultAssetRatioChange) / PRECISION;
vaultUtilization[_vault] = _prevVaultCbr > _vaultWhitelistCbr[_vault]
    ? _currentAssetsUtilized < _changeUtilizedState
        ? _currentAssetsUtilized
        : _currentAssetsUtilized - _changeUtilizedState
    : _currentAssetsUtilized + _changeUtilizedState;
```
It can be seen that if the cbr decreases and the decrease is more than the current utilization then the utilization stays the same, whereas in this case, the utilization should be 0 instead. Keeping it the same in scenarios where cbr decreases abruptly would be wrong as in the accounting for vault deposit/withdraw would be incorrect.

## Recommendation
Reset the vault utilization to 0 if the cbr decreased more than the vault's current utilization.
