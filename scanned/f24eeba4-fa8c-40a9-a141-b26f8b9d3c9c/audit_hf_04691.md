# [M] Incorrect spread liquidation for assets with 1e18 spreadPenalty

## Summary
Severity: Medium
Contest weight: 0.5847
Dataset id: 22455
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Assets for which spread is not supported are given a maintenance weight of 1e18
```solidity
function getSubAccountHealth(
    address subAccount,
    bool isInitial
) public view returns (int256 health) {
    ...
    uint256 spreadQuantity = spreadPenalties[spotAssetAddress]
        .maintenance == 1e18
        ? 0
        : _subAccountSpreadQuantity(spotBalance, perpPos);
```
Hence such positions from the view of liquidation must be treated as a separate spot + perp position instead of a normal spread. But when liquidating, this condition is not checked.
```solidity
function liquidateSubAccount(
    Structs.LiquidateSubAccount calldata txn
) external {
    ...
    // if naked perp positions exist, liquidate those first
    if (_userHasNakedPerps(liquidateeSubAccount)) revert
        Errors.LiquidateNakedPerpsFirst();
    _liquidateSpread(txn);
} else if (txn.liquidationMode == uint8(LiquidationMode.SPOT)) {
```
Hence a huge spread penalty (1e18) is incorrectly applied on the liquidation which results in the spot asset being liquidated at 0 price and the perp short position being liquidated at 2x price.
```solidity
function _getSpreadLiquidationPrice(
    address spotComponentAddress,
    uint256 oraclePrice,
    bool isSpot
) internal view returns (uint256 liquidationPrice) {
    uint64 spreadPenalty = _furnace()
        .getSpreadPenalty(spotComponentAddress)
        .maintenance;
    if (isSpot) {
        return oraclePrice.mul(1e18 - spreadPenalty);
    } else {
        // is short perp component, liquidate at a higher price
        return oraclePrice.mul(1e18 + spreadPenalty);
    }
}
```
This will cause the liquidatee to lose their funds at the gain of the liquidator.
Loss of funds for the liquidatee.

## Recommendation
Check whether spreadPenalty maintenance weight is 1e18 inside liquidateSubAccount and if yes disallow to liquidate as a spread.
