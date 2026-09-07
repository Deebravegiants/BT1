# [M] PricerInternal.sol#L49 : The price data returned from `_latestAnswer64x64` may not be a updated one (may not be a latest data)

## Summary
Severity: Medium
Chain: Smart contract
Component: 2022-09-knox
Published: 2022-10-18
Source: https://github.com/sherlock-audit/2022-09-knox-judging/issues/149
Type: sherlock-finding

## Details
ak1

high

# PricerInternal.sol#L49 : The price data returned from `_latestAnswer64x64` may not be a updated one (may not be a latest data)

## Summary
PricerInternal.sol#L49 : The price data returned from `_latestAnswer64x64` may not be a updated one (may not be a latest data)

## Vulnerability Detail
https://github.com/sherlock-audit/2022-09-knox/blob/main/knox-contracts/contracts/pricer/PricerInternal.sol#L49-L55

    function _latestAnswer64x64() internal view returns (int128) {
        (, int256 basePrice, , , ) = BaseSpotOracle.latestRoundData();
        (, int256 underlyingPrice, , , ) =
            UnderlyingSpotOracle.latestRoundData();


        return ABDKMath64x64.divi(underlyingPrice, basePrice);
    }

In above code, the price data from `BaseSpotOracle` , `UnderlyingSpotOracle` is directly used to return the data after dividing.
`return ABDKMath64x64.divi(underlyingPrice, basePrice);`
It is not always true that the price data that is received is latest one.

## Impact
Usage of stale data will not be healthy.
The received data could be too high or too low that could leave meaningful impact to the protocol also to the end user.

## Code Snippet
https://github.com/sherlock-audit/2022-09-knox/blob/main/knox-contracts/contracts/pricer/PricerInternal.sol#L49-L55

https://github.com/sherlock-audit/2022-09-knox/blob/main/knox-contracts/contracts/pricer/Pricer.sol#L25-L27

The function `getDeltaStrikePrice64x64` is using the price data.

https://github.com/sherlock-audit/2022-09-knox/blob/main/knox-contracts/contracts/pricer/Pricer.sol#L84


_Trimmed to 38 lines — full report: https://github.com/sherlock-audit/2022-09-knox-judging/issues/149_
