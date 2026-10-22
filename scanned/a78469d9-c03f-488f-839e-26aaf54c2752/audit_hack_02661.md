# [M] `_latestAnswer64x64()` can return an incorrect result and lead to stale prices being used in `Auction`

## Summary
Severity: Medium
Reporter: joestakey
Source: https://github.com/sherlock-audit/2022-09-knox/blob/main/knox-contracts/contracts/vault/VaultInternal.sol#L613-L619
Type: audit-issue

## Details
# `_latestAnswer64x64()` can return an incorrect result and lead to stale prices being used in `Auction`

## Summary
`PricerInternal._latestAnswer64x64()` does not check the return value, meaning it can return a [stale](https://docs.chain.link/docs/data-feeds/price-feeds/historical-data/#historical-rounds) price.

## Vulnerability Detail
`PricerInternal._latestAnswer64x64()` calls `BaseSpotOracle.latestRoundData()` and `UnderlyingSpotOracle.latestRoundData()` but does not check the round the price was fetched at. This means a stale price could be returned if there is high volatility (for instance with `wETH` or `wBTC`).

## Impact

A wrong price fetched in `PricerInternal._latestAnswer64x64()` results in `_setAuctionPrices()` setting incorrect [maxPrice64x64](https://github.com/sherlock-audit/2022-09-knox/blob/main/knox-contracts/contracts/vault/VaultInternal.sol#L613-L619) and [minPrice64x64](https://github.com/sherlock-audit/2022-09-knox/blob/main/knox-contracts/contracts/vault/VaultInternal.sol#L622-L628), setting the auction at incorrect prices, which leads to value leakage.

## Code Snippet
https://github.com/sherlock-audit/2022-09-knox/blob/main/knox-contracts/contracts/pricer/PricerInternal.sol#L50-L53

## Tool used

Manual Review

## Recommendation
Add additional checks to the return values of `latestRoundData`

```diff
-50:         (, int256 basePrice, , , ) = BaseSpotOracle.latestRoundData();
-51:         (, int256 underlyingPrice, , , ) =
+50:         (uint80 baseRoundID, int256 basePrice, uint256 baseTimestamp, uint80 baseAnsweredInRound) = BaseSpotOracle.latestRoundData();
+51:         (uint80 underlyingRoundID, int256 underlyingPrice, uint256 underlyingTimestamp, uint80 underlyingAnsweredInRound) =
52:             UnderlyingSpotOracle.latestRoundData();
+    require(baseAnsweredInRound >= baseRoundID && underlyingAnsweredInRound >=  underlyingRoundID, "Stale price");
+   require(baseTimestamp != 0 && underlyingTimestamp != 0 ,"Round not complete");
+   require(basePrice > 0 && underlyingPrice > 0,"wrong price");
```
