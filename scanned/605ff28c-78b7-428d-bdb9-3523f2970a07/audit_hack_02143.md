# [M] ChainLink price data could be stale

## Summary
Severity: Medium
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
# Handle

cmichel


# Vulnerability details

## Vulnerability Details
There is no check in `ExchangeRate.buildExchangeRate` if the return values indicate stale data. This could lead to stale prices according to the Chainlink documentation:
* [under current notifications: "if answeredInRound < roundId could indicate stale data."](https://docs.chain.link/docs/developer-communications#current-notifications)
* [under historical price data: "A timestamp with zero value means the round is not complete and should not be used."](https://docs.chain.link/docs/historical-price-data#solidity)

## Impact
Stale prices that do not reflect the current market price anymore could be used which would influence the exchange rate of the assets to ETH.
This could lead to issues with free collateral and lead to wrong liquidations/borrows.

## Recommendation
Add the recommended checks:

```solidity
(
    uint80 roundID,
    int256 price,
    ,
    uint256 timeStamp,
    uint80 answeredInRound
) = chainlink.latestRoundData();
require(
    timeStamp != 0,
    “ChainlinkOracle::getLatestAnswer: round is not complete”
);
require(
    answeredInRound >= roundID,
    “ChainlinkOracle::getLatestAnswer: stale data”
);
require(price != 0, "Chainlink Malfunction”);
```
