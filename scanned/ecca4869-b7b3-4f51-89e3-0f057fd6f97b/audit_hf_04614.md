# [M] M-13 | No Circuit Breaker Checks In ChainlinkOracle

## Summary
Severity: Medium
Contest weight: 0.0833
Dataset id: 22219
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
getPriceUSD18 returns _isBadData if the oracle price is stale. However, it doesn't consider the price going outside of the price range for the oracle's aggregator. The price will be capped between minAnswer and maxAnswer of the aggregator. This will result in a wrong price being used in the protocol. Even though most feeds have disabled their circuit breaker feature, there are still some that haven't, for example [CVX/ETH](https://etherscan.io/address/0xf1F7F7BFCc5E9D6BB8D9617756beC06A5Cbe1a49#readContract)

## Recommendation
If the price goes outside the aggregator range, set _isBadData to true
