# [M] AaveV3Adapter.sol#getRate may be outdated and stale.

## Summary
Severity: Medium
Chain: Smart contract
Component: 2022-10-union-finance
Published: 2022-11-04
Source: https://github.com/sherlock-audit/2022-10-union-finance-judging/issues/122
Type: sherlock-finding

## Details
ctf_sec

medium

# AaveV3Adapter.sol#getRate may be outdated and stale.

## Summary

AaveV3Adapter.sol#getRate may be outdated and stale.

## Vulnerability Detail

the function getRate from AaveV3Adapter.sol returns the currentLiqudityRate directly.

```solidity
function getRate(address tokenAddress) external view override returns (uint256) {
    LendingPool3.ReserveData memory reserveData = lendingPool.getReserveData(tokenAddress);
    return uint256(reserveData.currentLiquidityRate);
}
```

However, the reservedData.currentLiquidityRate may be outdated or stale.

Let us look into the struct of the ReserveData

```solidity
    struct ReserveData {
        //stores the reserve configuration
        ReserveConfigurationMap configuration;
        //the liquidity index. Expressed in ray
        uint128 liquidityIndex;
        //the current supply rate. Expressed in ray
        uint128 currentLiquidityRate;
        //variable borrow index. Expressed in ray
        uint128 variableBorrowIndex;
        //the current variable borrow rate. Expressed in ray
        uint128 currentVariableBorrowRate;
        //the current stable borrow rate. Expressed in ray
```

_Trimmed to 38 lines — full report: https://github.com/sherlock-audit/2022-10-union-finance-judging/issues/122_
