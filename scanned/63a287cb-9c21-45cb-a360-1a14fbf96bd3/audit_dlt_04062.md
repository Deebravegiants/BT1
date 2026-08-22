# [M] Using Balancer Math Functions With Incorrect Precision

## Summary
Severity: Medium
Chain: Smart contract
Component: 2022-09-notional
Published: 2022-10-13
Source: https://github.com/sherlock-audit/2022-09-notional-judging/issues/78
Type: sherlock-finding

## Details
xiaoming90

high

# Using Balancer Math Functions With Incorrect Precision

## Summary

The vault was found to perform Balancer math functions with incorrect precision.

## Vulnerability Detail

> Note: This issue affects MetaStable2 and Boosted3 balancer leverage vaults

When performing Balancer math functions, all amounts need to be in `BALANCER_PRECISION` as per the comment at Line 105 below. Therefore, in Line 106-109 below, the code attempts to convert the precision of `primaryAmount` and `secondaryAmount` to `BALANCER_PRECISION (1e18)` before passing them to the `StableMath._calcSpotPrice` function for computation. The `calculatedPairPrice` return value is then passed to `Stable2TokenOracleMath._checkPriceLimit` for additional validation.

Assume that either `primaryAmount` or `secondaryPrecision` is USDC OR any other tokens that their precision != `BALANCER_PRECISION (1e18)`.

USDC's precision is `1e6`, while BALANCER_PRECISION is `1e18`. Therefore, based on the formula in Lines 106-109 below, the USDC's precision will be converted to `1e18` before passing it to `StableMath._calcSpotPrice`.

https://github.com/sherlock-audit/2022-09-notional/blob/main/leveraged-vaults/contracts/vaults/balancer/internal/math/Stable2TokenOracleMath.sol#L89

```solidity
File: Stable2TokenOracleMath.sol
089:     function _validateSpotPriceAndPairPrice(
090:         StableOracleContext calldata oracleContext,
091:         TwoTokenPoolContext calldata poolContext,
092:         StrategyContext calldata strategyContext,
093:         uint256 primaryAmount, 
094:         uint256 secondaryAmount
095:     ) internal view {
096:         // Oracle price is always specified in terms of primary, so tokenIndex == 0 for primary
097:         uint256 spotPrice = _getSpotPrice(oracleContext, poolContext, 0);
098:         _checkPriceLimit(strategyContext, poolContext, spotPrice);
099: 
100:         // We always validate in terms of the primary here so it is the first value in the _balances array
101:         uint256 invariant = StableMath._calculateInvariant(
102:             oracleContext.ampParam, StableMath._balances(primaryAmount, secondaryAmount), true // round up
```

_Trimmed to 38 lines — full report: https://github.com/sherlock-audit/2022-09-notional-judging/issues/78_
