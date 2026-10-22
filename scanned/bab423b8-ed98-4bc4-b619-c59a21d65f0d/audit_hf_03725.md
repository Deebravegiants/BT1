# [M] Positions cannot be liquidated once the oracle price drops to zero

## Summary
Severity: Medium
Contest weight: 0.5714
Dataset id: 19854
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In the unlikely event that the price of an asset reaches zero, there is no way to liquidate the position, because both usages of oracles will revert. Zero is treated as an invalid value, for both index oracle prices, as well as position prices.

Positions won't be liquidatable, at an extremely critical moment that they should be liquidatable. Losses and fees will grow and the exchange will become insolvent.

The Chainlink oracle rejects prices of zero:
```solidity
// File: gmx-synthetics/contracts/oracle/Oracle.sol : Oracle._setPricesFromPriceFeeds()
(
    /* uint80 roundID */,
    int256 _price,
    /* uint256 startedAt */,
    /* uint256 timestamp */,
    /* uint80 answeredInRound */
) = priceFeed.latestRoundData();
uint256 price = SafeCast.toUint256(_price);
uint256 precision = getPriceFeedMultiplier(dataStore, token);
price = price * precision / Precision.FLOAT_PRECISION;
if (price == 0) {
    revert EmptyFeedPrice(token);
}
```
cts/oracle/Oracle.sol#L571-L587

As does the usage of off-chain oracle prices:
```solidity
// File: gmx-synthetics/contracts/oracle/Oracle.sol : Oracle.getLatestPrice()
if (!secondaryPrice.isEmpty()) {
    return secondaryPrice;
}
Price.Props memory primaryPrice = primaryPrices[token];
if (!primaryPrice.isEmpty()) {
    return primaryPrice;
}
revert OracleUtils.EmptyLatestPrice(token);
}
```
cts/oracle/Oracle.sol#L341-L356

## Recommendation
Provide a mechanism for positions to be liquidated even if the price reaches zero
