# [M] `PendlePowerManager` is incompatible with `PendleRouterV3`

## Summary
Severity: Medium
Chain: Smart contract
Component: 2024-02-wise-lending
Published: 2024-03-10
Source: https://github.com/code-423n4/2024-02-wise-lending-findings/issues/133
Type: code-finding

## Details
# Lines of code

https://github.com/pendle-finance/pendle-core-v2-public/blob/main/contracts/router/ActionAddRemoveLiqV3.sol#L166-L172
https://github.com/pendle-finance/pendle-core-v2-public/blob/main/contracts/router/ActionAddRemoveLiqV3.sol#L444-L449
https://github.com/code-423n4/2024-02-wise-lending/blob/main/contracts/PowerFarms/PendlePowerFarm/PendlePowerFarmLeverageLogic.sol#L467-L482
https://github.com/code-423n4/2024-02-wise-lending/blob/main/contracts/PowerFarms/PendlePowerFarm/PendlePowerFarmLeverageLogic.sol#L165-L171


# Vulnerability details

## Impact

`PendlePowerManager` is incompatible with the latest deployment of `PendleRouter` and will cause reverts when attempting to open a farm position.

## Proof of Concept

The latest deployment of the Pendle router, `PendleRouterV3`, is incompatible with the `PendlePowerManager` contract. The sponsor is expecting full compatibility with both but this is not the case here. The problem stems from the calls made to `PENDLE_ROUTER.removeLiquiditySingleSy()` and `PENDLE_ROUTER.addLiquiditySingleSy()`:

```solidity
function _logicOpenPosition(
    bool _isAave,
    uint256 _nftId,
    uint256 _depositAmount,
    uint256 _totalDebtBalancer,
    uint256 _allowedSpread
)
    internal
{
    // ...
    (
        uint256 netLpOut
        ,
    ) = PENDLE_ROUTER.addLiquiditySingleSy(
        {
            _receiver: address(this),
            _market: address(PENDLE_MARKET),
            _netSyIn: syReceived,
            _minLpOut: 0,
```

_Trimmed to 38 lines — full report: https://github.com/code-423n4/2024-02-wise-lending-findings/issues/133_
