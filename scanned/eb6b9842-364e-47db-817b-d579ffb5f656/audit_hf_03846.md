# [M] outdated variable is not effective to check multiple chainlink feeds

## Summary
Severity: Medium
Contest weight: 0.4591
Dataset id: 20097
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In ChainlinkOraclePivot, it uses one outdated variable to check if the two price
feeds are outdated. However, this is not effective because the price feeds have
different update frequencies.
Let's have an example:
In Polygon mainnet, ChainlinkOraclePivot uses two Chainlink price feeds:
MATIC/ETH and ETH/USD.
The setup can be the same in this test case:
es/test/foundry/ChainLinkOraclePivotWrapper.t.sol#L49-L63
We can see that
• priceFeedA: MATIC/ETH price feed has a heartbeat of 86400s
(https://data.chain.link/polygon/mainnet/crypto-eth/matic-eth).
• priceFeedB: ETH/USD price feed has a heartbeat of 27s
(https://data.chain.link/polygon/mainnet/crypto-usd/eth-usd).
In function _getLatestRoundData, both price feeds use the same outdated variable.
• If we set the outdated variable to 27s, the priceFeedA will revert most of the
time since it is too short for the 86400s heartbeat.
• If we set the outdated variable to 86400s, the priceFeedB can have a very
outdated value without revert.
```solidity
try priceFeedA.latestRoundData() returns (
    uint80,
    int256 price,
    uint256,
    uint256 updatedAt,
    uint80
) {
    require(
        block.timestamp - updatedAt <= outdated, // solhint-disable-line not-rely-on-time
        "ChainLinkOracle: priceFeedA outdated."
    );
    priceA = SafeCast.toUint256(price);
} catch {
    revert("ChainLinkOracle: price feed A call failed.");
}
try priceFeedB.latestRoundData() returns (
    uint80,
    int256 price,
    uint256,
    uint256 updatedAt,
    uint80
) {
    require(
        block.timestamp - updatedAt <= outdated, // solhint-disable-line not-rely-on-time
        "ChainLinkOracle: priceFeedB outdated."
    );
    priceB = SafeCast.toUint256(price);
} catch {
    revert("ChainLinkOracle: price feed B call failed.");
}
```
es/contracts/oracles/ChainLinkOraclePivot.sol#L239-L271
The outdated variable is not effective to check the timeliness of prices. It can allow
stale prices in one price feed or always revert in another price feed.

## Recommendation
Having two outdated values for each price feed A and B.
