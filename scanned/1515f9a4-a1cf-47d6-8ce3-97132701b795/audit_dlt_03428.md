# [M] Chainlink connector doesn’t check for the Min / Max prices returned

## Summary
Severity: Medium
Chain: Smart contract
Component: 2024-04-noya
Published: 2024-05-17
Source: https://github.com/code-423n4/2024-04-noya-findings/issues/1415
Type: code-finding

## Details
# Lines of code

https://github.com/code-423n4/2024-04-noya/blob/9c79b332eff82011dcfa1e8fd51bad805159d758/contracts/helpers/valueOracle/oracles/ChainlinkOracleConnector.sol#L115-L134


# Vulnerability details

# **Vulnerability Detail**

When the price of an asset deviates significantly from a predefined price range, Chainlink aggregators activate a circuit breaker mechanism. In situations like the crash of LUNA, this mechanism causes the oracle to consistently return the minimum price instead of the actual price of the asset. Consequently, users can continue to borrow against the asset, but at an incorrect price. This scenario occurred on Venus on the Binance Smart Chain (BSC) during the collapse of LUNA.

The ChainLink Oracle Connector doesn’t implement any checks to handle such scenarios.

# **Proof of Concept**

The ChainlinkFeedRegistry#latestRoundData function retrieves round data from the associated aggregator. These Chainlink aggregators include circuit breakers for minPrice and maxPrice, ensuring that if the asset's price falls below the minPrice, the protocol will continue to value the token at minPrice rather than its actual value. This scenario enables users to borrow significant amounts of bad debt, potentially leading to bankruptcy for the protocol.

For instance, consider TokenA with a minPrice set at $1. If the price of TokenA drops to $0.10, the aggregator still reports $1

# **Impact**

The chainlink could return incorrect prices.

# **Recommendation**

ChainlinkAdapterOracle should check the returned answer against the minPrice/maxPrice and revert if the answer is outside of the bounds:

```solidity
    (, int256 answer, , uint256 updatedAt, ) = registry.latestRoundData(
        token,
        USD
    );
+   if (answer >= maxPrice or answer <= minPrice) revert();
```

# **References**

https://solodit.xyz/issues/m-16-chainlinkadapteroracle-will-return-the-wrong-price-for-asset-if-underlying-aggregator-hits-minanswer-sherlock-blueberry-blueberry-git

_Trimmed to 38 lines — full report: https://github.com/code-423n4/2024-04-noya-findings/issues/1415_
