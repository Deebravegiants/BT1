# [H] Disabling an asset via STBL_Register::disableAsset with active deposits can DOS user withdrawals

## Summary
Severity: High
Contest weight: 0.0000
Dataset id: 23375
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Description: The STBL_Register::disableAsset does not check for active deposits before disabling an asset, creating a Denial of Service (DOS) condition where users cannot withdraw their deposited funds.
STBL_Register::disableAsset only checks if the asset is currently enabled but ignores whether there are active user deposits:
// STBL_Register.sol - disableAsset()
```solidity
function disableAsset(uint256 _id) external onlyRole(REGISTER_ROLE) {
    if (assetData[_id].status != AssetStatus.ENABLED)
        revert STBL_AssetNotActive();
    assetData[_id].status = AssetStatus.DISABLED; // @audit does not check for active deposits
    emit AssetStateUpdateEvent(_id, true);
}
```
However, the withdrawal flow requires the asset to be in ENABLED status to complete successfully. The STBL_Core::exit function uses the isValidIssuer modifier which checks asset status:
// STBL_Core.sol
```solidity
modifier isValidIssuer(uint256 _assetID) {
    AssetDefinition memory AssetData = registry.fetchAssetData(_assetID);
    if (!AssetData.isIssuer(_msgSender())) revert STBL_UnauthorizedIssuer();
    if (!AssetData.isActive()) revert STBL_AssetDisabled(_assetID); // @audit blocks exit on disabled
    assets,!
    _;
}
```
```solidity
function exit(uint256 _assetID, address _from, uint256 _tokenID, uint256 _value)
    external isValidIssuer(_assetID) { // @audit Modifier prevents exit on disabled assets
    // ... burn tokens and decrement deposits
}
```
Impact: Disabled asset with active deposits prevents user withdrawals.

## Recommendation
Consider preventing disabling of assets with active deposits.
