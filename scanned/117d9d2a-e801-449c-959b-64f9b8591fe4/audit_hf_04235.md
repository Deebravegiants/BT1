# [M] M-13 | Lack of Pyth Confidence Interval Check

## Summary
Severity: Medium
Contest weight: 0.1100
Dataset id: 21131
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Currently the system uses parsePriceFeedUpdatesUnique to get the first unique price for the given time period. Pyth provides instant prices, but because market price discovery takes time and happens gradually over all of the markets Pyth has implemented confidence in their system. For example, the returned price for ETH can be $2000 with confidence of +-20 USD. This means the real price of ETH can range from $1980 to $2020. Currently there are no checks for confidence, which can lead to users not being liquidated in time, lowering the profits for LP providers, or putting them in debt.

## Recommendation
Consider using the confidence intervals as described in Pyth’s [best practices](https://docs.pyth.network/price-feeds/best-practices). If someone wants to open a derivative contract, their collateral may be valued at the lower price. However, if deciding whether someone's margin limits were violated, value their outstanding leveraged position at the higher price.
