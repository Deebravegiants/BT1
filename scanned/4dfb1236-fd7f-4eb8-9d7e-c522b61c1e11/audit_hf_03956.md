# [M] Vault cannot be added back into the vault

## Summary
Severity: Medium
Contest weight: 0.6831
Dataset id: 20302
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
When removing a vault from the registry, all states related to the vaults such as the _vaults, _assets, _vaultsByAsset are cleared except the _vaultsByType state.
```solidity
function removeVault(address vaultAddress) external onlyUpdater {
    Errors.verifyNotZero(vaultAddress, "vaultAddress");
    // remove from vaults list
    if (!_vaults.remove(vaultAddress)) revert VaultNotFound(vaultAddress);
    address asset = ILMPVault(vaultAddress).asset();
    // remove from assets list if this was the last vault for that asset
    if (_vaultsByAsset[asset].length() == 1) {
        //slither-disable-next-line unused-return
        _assets.remove(asset);
    }
    // remove from vaultsByAsset mapping
    if (!_vaultsByAsset[asset].remove(vaultAddress)) revert VaultNotFound(vaultAddress);

    emit VaultRemoved(asset, vaultAddress);
}
```
sol#L64-L82
The uncleared _vaultsByType state will cause the addVault function to revert when trying to add the vault back into the registry even though the vault does not exist in the registry anymore.
```solidity
if (!_vaultsByType[vaultType].add(vaultAddress)) revert VaultAlreadyExists(vaultAddress);
```
sol#L59
The addVault function is broken in the edge case when the updater tries to add the vault back into the registry after removing it. It affects all the operations of the protocol that rely on the vault registry.

## Recommendation
Clear the _vaultsByType state when removing the vault from the registry.
```solidity
function removeVault(address vaultAddress) external onlyUpdater {
    Errors.verifyNotZero(vaultAddress, "vaultAddress");
    ILMPVault vault = ILMPVault(vaultAddress);
    bytes32 vaultType = vault.vaultType();
    // remove from vaults list
    if (!_vaults.remove(vaultAddress)) revert VaultNotFound(vaultAddress);

    address asset = ILMPVault(vaultAddress).asset();
    // remove from assets list if this was the last vault for that asset
    if (_vaultsByAsset[asset].length() == 1) {
        //slither-disable-next-line unused-return
        _assets.remove(asset);
    }
    // remove from vaultsByAsset mapping
    if (!_vaultsByAsset[asset].remove(vaultAddress)) revert VaultNotFound(vaultAddress);

    if (!_vaultsByType[vaultType].remove(vaultAddress)) revert VaultNotFound(vaultAddress);

    emit VaultRemoved(asset, vaultAddress);
}
```
