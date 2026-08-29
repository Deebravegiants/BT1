# [M] Stale data in Oracle data feed

## Summary
Severity: Medium
Chain: Smart contract
Component: 2022-09-knox
Published: 2022-10-18
Source: https://github.com/sherlock-audit/2022-09-knox-judging/issues/152
Type: sherlock-finding

## Details
ArbitraryExecution

medium

### Stale data in Oracle data feed

The \_latestAnswer64x64 function in the [PricerInternal](https://github.com/sherlock-audit/2022-09-knox-pbwaffles/blob/e7ad5b071a83482406366e6dbbbbbc65b09c1e04/knox-contracts/contracts/pricer/PricerInternal.sol#L49-L55) contract is used to determine the current price for the underlying asset. There is however no check to ensure that the data returned is recent enough to be valid.

    function _latestAnswer64x64() internal view returns (int128) {
        (, int256 basePrice, , , ) = BaseSpotOracle.latestRoundData();
        (, int256 underlyingPrice, , , ) =
            UnderlyingSpotOracle.latestRoundData();


        return ABDKMath64x64.divi(underlyingPrice, basePrice);
    }

#### Recommendation

Use best practices to ensure that the data is valid. For example, consider checking against the updatedAt variable returned in the result data.


Duplicate of #137
