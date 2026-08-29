# [M] Stale price can be used in `getValueFromChainlinkFeed` function

## Summary
Severity: Medium
Chain: Smart contract
Component: 2024-04-noya
Published: 2024-05-17
Source: https://github.com/code-423n4/2024-04-noya-findings/issues/1501
Type: code-finding

## Details
# Lines of code

https://github.com/code-423n4/2024-04-noya/blob/cc3854f634a72bd4a8b597021887088ca2d6d29f/contracts/helpers/valueOracle/oracles/ChainlinkOracleConnector.sol#L56-L62
https://github.com/code-423n4/2024-04-noya/blob/cc3854f634a72bd4a8b597021887088ca2d6d29f/contracts/helpers/valueOracle/oracles/ChainlinkOracleConnector.sol#L115-L135


# Vulnerability details

## Impact
According to the following `updateChainlinkPriceAgeThreshold` function, the minimum possible `chainlinkPriceAgeThreshold` would be 61 seconds. However, there are Chainlink oracles that have heartbeat that is less than 61 seconds; these oracles are essential for providing prices for the ERC20 tokens that should be supported by this protocol in which these tokens have the in scope token behaviors and exist on the intended chains described in https://code4rena.com/audits/2024-04-noya. For example, the USDC / USD Chainlink oracle on Polygon has a heartbeat of 27 seconds according to the popup of the Trigger parameters section's information icon in https://data.chain.link/feeds/polygon/mainnet/usdc-usd.

https://github.com/code-423n4/2024-04-noya/blob/cc3854f634a72bd4a8b597021887088ca2d6d29f/contracts/helpers/valueOracle/oracles/ChainlinkOracleConnector.sol#L56-L62
```solidity
    function updateChainlinkPriceAgeThreshold(uint256 _chainlinkPriceAgeThreshold) external onlyMaintainer {
        if (_chainlinkPriceAgeThreshold <= 1 hours || _chainlinkPriceAgeThreshold >= 10 days) {
            revert NoyaChainlinkOracle_INVALID_INPUT();
        }
        chainlinkPriceAgeThreshold = _chainlinkPriceAgeThreshold;
        ...
    }
```

For Chainlink oracles that have heartbeat that is less than 61 seconds,`block.timestamp - updatedAt > chainlinkPriceAgeThreshold` in the following `getValueFromChainlinkFeed` function can be false when the `updatedAt` actually corresponds to a stale price. For instance, when the `updatedAt` returned by the USDC / USD Chainlink oracle on Polygon is `block.timestamp - 27 * 2`, a newer price should be reported at `block.timestamp - 27` but that did not happen so the corresponding price reported at `block.timestamp - 27 * 2` is already stale; yet, because `block.timestamp - updatedAt > chainlinkPriceAgeThreshold` is false for such `updatedAt`, the `getValueFromChainlinkFeed` function does not revert with the `NoyaChainlinkOracle_DATA_OUT_OF_DATE` error. As a result, the stale price is used in the `getValueFromChainlinkFeed` function.

Moreover, the `chainlinkPriceAgeThreshold` being set to only one value can fail to accommodate all Chainlink oracles that are intended to be supported by the `ChainlinkOracleConnector` contract when these oracles have different heartbeats. In this case, the `chainlinkPriceAgeThreshold` that ensures that one oracle's price is not stale can fail to ensure that the other oracle's price is not stale if the latter oracle's heartbeat is smaller than the former's.

https://github.com/code-423n4/2024-04-noya/blob/cc3854f634a72bd4a8b597021887088ca2d6d29f/contracts/helpers/valueOracle/oracles/ChainlinkOracleConnector.sol#L115-L135
```solidity
    function getValueFromChainlinkFeed(
        AggregatorV3Interface source,
        uint256 amountIn,
        uint256 sourceTokenUnit,
        bool isInverse
    ) public view returns (uint256) {
        int256 price;
        uint256 updatedAt;
        (, price,, updatedAt,) = source.latestRoundData();
        uint256 uintprice = uint256(price);
```

_Trimmed to 38 lines — full report: https://github.com/code-423n4/2024-04-noya-findings/issues/1501_
