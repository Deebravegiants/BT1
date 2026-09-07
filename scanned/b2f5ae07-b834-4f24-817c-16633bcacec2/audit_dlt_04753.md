# [M] Insufficient validation in Oracle price data feed

## Summary
Severity: Medium
Chain: Smart contract
Component: 2022-09-knox
Published: 2022-10-18
Source: https://github.com/sherlock-audit/2022-09-knox-judging/issues/81
Type: sherlock-finding

## Details
jayphbee

medium

# Insufficient validation in Oracle price data feed

## Summary

When fetching prices from `latestRoundData`, there is not enough check to ensure the price returned is not stale.

## Vulnerability Detail

The `PricerInternal.sol#_latestAnswer64x64` function fetches oracle price from Chainlink using `latestRoundData`, but it doesn't check if the returned `basePrice` is stale or not.

## Impact

This may lead to stale price to be used.

## Code Snippet
https://github.com/sherlock-audit/2022-09-knox/blob/main/knox-contracts/contracts/pricer/PricerInternal.sol#L49-L55
```solidity
    function _latestAnswer64x64() internal view returns (int128) {
        (, int256 basePrice, , , ) = BaseSpotOracle.latestRoundData();
        (, int256 underlyingPrice, , , ) =
            UnderlyingSpotOracle.latestRoundData();

        return ABDKMath64x64.divi(underlyingPrice, basePrice);
    }
```

## Tool used

Manual Review

## Recommendation

change the implementation of `PricerInternal.sol#_latestAnswer64x64` to:


_Trimmed to 38 lines — full report: https://github.com/sherlock-audit/2022-09-knox-judging/issues/81_
