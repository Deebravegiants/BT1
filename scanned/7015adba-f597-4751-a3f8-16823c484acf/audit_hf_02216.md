# [M] Owner Address Centralization Risk

## Summary
Severity: Medium
Contest weight: 0.4608
Dataset id: 12257
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The Holdefi protocol has the notion of an administrator or owner who has exclusive access to critical functions. This is implemented using the onlyOwner modifier shown below, which is enforced on several critical functions that are used to add/remove/change markets/collateral/funds and access/parameters (some of which are shown below).

```solidity
/// @notice
/// Throws if called by any account other than the owner
modifier onlyOwner() {
    require(msg.sender == owner, "Sender should be owner");
}

/// @notice
/// Activate a market asset
/// @dev
/// Can only be called by the owner
/// @param market
/// Address of the given market
function activateMarket(address market) public onlyOwner marketIsExist(market) {
    activateMarketInternal(market);
}

/// @notice
/// Deactivate a market asset
/// @dev
/// Can only be called by the owner
/// @param market
/// Address of the given market
function deactivateMarket(address market) public onlyOwner marketIsExist(market) {
    marketAssets[market].isActive = false;
    emit MarketActivationChanged(market, false);
}

/// @notice
/// Activate a collateral asset
/// @dev
/// Can only be called by the owner
/// @param collateral
/// Address the given collateral
function activateCollateral(address collateral) public onlyOwner collateralIsExist(collateral) {
    activateCollateralInternal(collateral);
}
/// @notice
/// Deactivate a collateral asset
/// @dev
/// Can only be called by the owner
/// @param collateral
/// Address of the given collateral
function deactivateCollateral(address collateral) public onlyOwner collateralIsExist(collateral) {
    collateralAssets[collateral].isActive = false;
    emit CollateralActivationChanged(collateral, false);
}
```

risk in the event of the private key getting compromised or lost. This should ideally be a multi-sig contract account with multiple owners (e.g. 3 of 5) required to authorize transactions from that account. That will avoid central points of failure and reduce the risk.

## Recommendation
Owner address should be a multi-sig contract account (not EOA) with a reasonable threshold of owners (e.g. 3 of 5) required to authorize transactions.
