# [M] Fixed heartbeat used for price validation is too stale for some tokens

## Summary
Severity: Medium
Contest weight: 0.4744
Dataset id: 21270
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The vulnerability stems from a hard‑coded heartbeat constant (MAX_TIME_WINDOW) that is used to reject price data older than 24 hours plus 60 seconds. This constant is applied uniformly to every token and every blockchain, ignoring the fact that Chainlink price feeds have different update frequencies depending on the token‑chain pair. For tokens such as ezETH on Arbitrum, the underlying price feed updates roughly every six hours, which means that after a full day the most recent price will be older than the 24‑hour window and the contract will treat it as stale. The contract’s getMintRate (and similar lookup functions) checks the timestamp returned by the feed and reverts with OraclePriceExpired when the timestamp is earlier than block.timestamp‑MAX_TIME_WINDOW. Consequently, a user attempting to mint or redeem on a chain where the feed updates less frequently than the hard‑coded window will encounter a revert, or the protocol may fall back to using a price that is no longer current if the revert is not properly handled. This breaks the business assumption that the oracle always provides fresh data, leading to situations where users see no change in their balances, receive a “price expired” error, or are forced to wait for an extended period before the operation succeeds. The issue was discovered during a Code4rena audit by comparing the contract’s stale‑period logic with the documented update intervals of the relevant Chainlink feeds. It is subtle because the 24‑hour window appears reasonable for many feeds, so the problem only manifests for specific token‑chain combinations and shows up as intermittent transaction failures rather than a constant bug. To remediate, the contract should store a per‑token, per‑chain heartbeat value in a mapping or make the stale period configurable, allowing each feed’s actual update cadence to be respected. This change restores the intended accounting guarantees, ensures that price data used for minting and redemption is fresh, and prevents users from experiencing unexpected reverts or inaccurate pricing.

## Proof of Concept
In both `RenzoOracle` and `RenzoOracleL2`, the heartbeat period `MAX_TIME_WINDOW` is set to `86400 + 60; // 24 hours + 60 seconds`. In the functions `RenzoOracleL2::getMintRate` and `RenzoOracle::lookupTokenValue`, a validation checks sees if the price data fed by Chainlink’s price feed aggregators is stale depending if the period of `24 hours + 60 seconds` has passed. Example:

```solidity
    function getMintRate() public view returns (uint256, uint256) {
        (, int256 price, , uint256 timestamp, ) = oracle.latestRoundData();
        if (timestamp < block.timestamp - MAX_TIME_WINDOW) revert OraclePriceExpired();
```

The problem is that depending on the token and the chain, the same period can be considered too small or too stale.

Let’s consider the ezETH/ETH oracles on different chains:

  * On Ethereum, the oracle will update the price data every [`~24 hours`](https://data.chain.link/feeds/ethereum/mainnet/ezeth-eth).
  * On Arbitrum, the oracle will update the price data every [`~6 hours`](https://data.chain.link/feeds/arbitrum/mainnet/ezeth-eth-exchange-rate).
  * On Linea, the oracle will update the price data every [`24 hours`](https://data.chain.link/feeds/linea/mainnet/ezeth-eth).

This means that on Arbitrum, `24 hours` can be considered too large for the stale period which will cause the function `RenzoOracleL2::getMintRate` to return stale data.

## Recommendation
It is recommended to store a mapping that would record the heartbeat parameter for the stale period of each token and for every different chain.
