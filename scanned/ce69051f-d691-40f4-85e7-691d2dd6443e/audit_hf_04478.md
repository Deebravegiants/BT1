# [M] M-03 | Deprecated latestAnswer Used In _check Function

## Summary
Severity: Medium
Contest weight: 0.0721
Dataset id: 21976
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The _check function in the KeeperProxy contract checks the price difference between the given price and the Chainlink price. The issue is that the Chainlink price is fetched using the latestAnswer function, which is deprecated and should no longer be used [reference](https://docs.chain.link/data-feeds/api-reference#latestanswer).

## Recommendation
The _check function should instead use the latestRoundData function for price retrieval, as it allows for additional validations to ensure that the price data is current and reliable. Refer to the [Chainlink documentation](https://docs.chain.link/data-feeds/using-data-feeds#solidity) for implementation details.
