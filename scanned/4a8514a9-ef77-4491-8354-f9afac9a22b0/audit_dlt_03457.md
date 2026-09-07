# [M] `OracleManagerChainlink` price data could be stale

## Summary
Severity: Medium
Chain: Smart contract
Component: 2021-08-floatcapital
Published: 2021-08-11
Source: https://github.com/code-423n4/2021-08-floatcapital-findings/issues/119
Type: code-finding

## Details
# Handle

cmichel


# Vulnerability details

There is no check in `OracleManagerChainlink._getLatestPrice` if the return values indicate stale data. This could lead to stale prices according to the Chainlink documentation:
* [under current notifications: "if answeredInRound < roundId could indicate stale data."](https://docs.chain.link/docs/developer-communications#current-notifications)
* [under historical price data: "A timestamp with zero value means the round is not complete and should not be used."](https://docs.chain.link/docs/historical-price-data#solidity)

## Impact
Stale prices that do not reflect the current market price anymore could be used for the `OracleManagerChainlink` price index which would wrongly influence the price of long/short tokens.

## Recommendation
Add the recommended checks:

```solidity
(
    uint80 roundID,
    int256 price,
    ,
    uint256 timeStamp,
    uint80 answeredInRound
) = chainlinkOracle.latestRoundData();
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
