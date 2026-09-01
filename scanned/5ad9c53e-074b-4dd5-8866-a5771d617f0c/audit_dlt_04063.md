# [M] Vulnerable Internal Price Oracle

## Summary
Severity: Medium
Chain: Smart contract
Component: 2022-09-notional
Published: 2022-10-13
Source: https://github.com/sherlock-audit/2022-09-notional-judging/issues/77
Type: sherlock-finding

## Details
xiaoming90

high

# Vulnerable Internal Price Oracle

## Summary

The internal price oracle within the vault does not reflect the true value of the assets. As such, the assets might be overvalued or undervalued leading to an array of issues.

## Vulnerability Detail

> Note: This issue affects the MetaStable2 balancer leverage vault

One of the key questions to ask when designing a price oracle is what if the price returned is absurdly small or absurdly large, and what are the mitigation controls in place if this happens?

Based on the current implementation of stETH/ETH balancer leverage vault, the price pair is computed based on a weighted average of Balancer Oracle and Chainlink as shown below.

https://github.com/sherlock-audit/2022-09-notional/blob/main/leveraged-vaults/contracts/vaults/balancer/internal/pool/TwoTokenPoolUtils.sol#L72

```solidity
File: TwoTokenPoolUtils.sol
066:     /// @notice Gets the oracle price pair price between two tokens using a weighted
067:     /// average between a chainlink oracle and the balancer TWAP oracle.
068:     /// @param poolContext oracle context variables
069:     /// @param oracleContext oracle context variables
070:     /// @param tradingModule address of the trading module
071:     /// @return oraclePairPrice oracle price for the pair in 18 decimals
072:     function _getOraclePairPrice(
073:         TwoTokenPoolContext memory poolContext,
074:         OracleContext memory oracleContext, 
075:         ITradingModule tradingModule
076:     ) internal view returns (uint256 oraclePairPrice) {
077:         // NOTE: this balancer price is denominated in 18 decimal places
078:         uint256 balancerWeightedPrice;
079:         if (oracleContext.balancerOracleWeight > 0) {
080:             uint256 balancerPrice = BalancerUtils._getTimeWeightedOraclePrice(
081:                 address(poolContext.basePool.pool),
```

_Trimmed to 38 lines — full report: https://github.com/sherlock-audit/2022-09-notional-judging/issues/77_
