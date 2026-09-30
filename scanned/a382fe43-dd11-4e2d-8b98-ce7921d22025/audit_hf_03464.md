# [M] OCL-1 | Chainlink Feed Manipulation

## Summary
Severity: Medium
Contest weight: 0.0941
Dataset id: 18887
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In the event that a conﬁgured Chainlink price feed is outdated the order execution transaction will not occur due to a PriceFeedNotUpdated revert. A malicious trader may observe that the price feed is outdated and submit a market order that includes a token requiring that price feed. The trader’s order will not be executed as the price feed is outdated. The trader can then observe that the chainlink prices have been updated with a transmit transaction and choose to cancel their order if price has not moved favorably in the time that the price feed was outdated.

## Recommendation
Carefully monitor outdated Chainlink price feeds and consider implementing logic to freeze/cancel orders that cannot be executed.
