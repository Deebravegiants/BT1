# [M] Price Oracle contract does not work in Arbi-

## Summary
Severity: Medium
Contest weight: 0.4180
Dataset id: 20049
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The PriceOracle contract relies on the Chainlink Oracle FeedRegistry to get the price of tokens. However, the FeedRegistry is not available in L2 networks such as Arbitrum and Optimism. This means that the PriceOracle contract will fail to return the price of tokens in these networks. The PriceOracle contract uses the Chainlink Oracle FeedRegistry to get the latest round data for a pair of tokens.

```solidity
(int256 price,) = registry.latestRoundData(base, quote);
```

/oracle/PriceOracle.sol#L67 The Iron Bank is deployed in mainnet, Arbitrum and Optimism. However, according to the Chainlink documentation, the FeedRegistry is only available in mainnet and not in Arbitrum and Optimism. https://docs.chain.link/data-feeds/feed-registry#contract-addresses This means that the PriceOracle contract will not be able to get the price of tokens in these L2 networks. This will affect the functionalities of the protocol that depend on the token price, such as liquidation. /pool/IronBank.sol#L827-L828 The PriceOracle contract will not function properly in L2 networks. This will break the protocol functions that rely on the token price.

## Recommendation
Reimplement the PriceOracle contract by reading the price feed from AggregatorV3Interface instead of FeedRegistry. Example: https://docs.chain.link/data-feeds/l2-sequencer-feeds#example-code
