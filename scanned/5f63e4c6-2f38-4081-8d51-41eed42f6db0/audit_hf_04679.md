# [M] In LeverageModule.executeOpen/executeAdjust, checkSkewMax is called before updateGlobalPositionData

## Summary
Severity: Medium
Contest weight: 0.6032
Dataset id: 22431
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
/flatcoin-v1/src/FlatcoinVault.sol#L296) is used to assert that the system will not be too skewed towards longs after additional skew is added. However, the stableCollateralTotal used by this function is a variable that will be updated by updateGlobalPositionData(FlatcoinStructs.GlobalPositionData storage _globalPositions, int256 price, int256 marginDelta, int256 additionalSizeDelta) in flatcoin-v1/src/FlatcoinVault.sol#L205). Therefore, checkSkewMax should be executed after updateGlobalPositionData. Otherwise, there is no guarantee whether newly opened positions will make the system more skew towards long side.
File: flatcoin-v1\src\LeverageModule.sol
```solidity
function executeOpen(
    address _account,
    address _keeper,
    FlatcoinStructs.Order calldata _order
) external whenNotPaused onlyAuthorizedModule returns (uint256 _newTokenId) {
    vault.checkSkewMax({additionalSkew: announcedOpen.additionalSize});

    {
        // The margin change is equal to funding fees accrued to longs and the margin deposited by the trader.
        vault.updateGlobalPositionData({
            price: entryPrice,
            marginDelta: int256(announcedOpen.margin),
            additionalSizeDelta: int256(announcedOpen.additionalSize)
        });
    }
}
```
/flatcoin-v1/src/FlatcoinVault.sol#L296-L307) internally calculates longSkewFraction by the formula ((_globalPositions.sizeOpenedTotal + _additionalSkew) * 1e18) / stableCollateralTotal. This function guarantees that longSkewFraction will not exceed skewFractionMax ([). However, stableCollateralTotal will be updated by _updateGlobalPositionData(). When profitLossTotal is positive value, then stableCollateralTotal will decrease. When profitLossTotal is negative value, then stableCollateralTotal will increase. Assume the following: We explain it in two situations:
1. checkSkewMax is called before updateGlobalPositionData.
2. checkSkewMax is called after updateGlobalPositionData.
Therefore, this new position should not be allowed to open, as this will only make the system more skewed towards the long side. The stableCollateralTotal used by checkSkewMax is the value of the total profit that has not yet been settled, which is old value. In this way, when the price of collateral rises, it will cause the system to be more skewed towards the long side.

## Recommendation
File: flatcoin-v1\src\LeverageModule.sol
```solidity
function executeOpen(
    address _account,
    address _keeper,
    FlatcoinStructs.Order calldata _order
) external whenNotPaused onlyAuthorizedModule returns (uint256 _newTokenId) {
    {
        // The margin change is equal to funding fees accrued to longs and the margin deposited by the trader.
        vault.updateGlobalPositionData({
            price: entryPrice,
            marginDelta: int256(announcedOpen.margin),
            additionalSizeDelta: int256(announcedOpen.additionalSize)
        });
    }

    vault.checkSkewMax(0); //0 means that vault.updateGlobalPositionData has added announcedOpen.additionalSize.
}
```
Also, if announcedAdjust.additionalSizeAdjustment is greater than 0 in flatcoin-v1/src/LeverageModule.sol#L166, similar fix is required.
