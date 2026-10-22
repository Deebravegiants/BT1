# [M] Pyth price feed maximum age too high allows stale price data

## Summary
Severity: Medium
Contest weight: 0.3946
Dataset id: 5758
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
When using Pyth price feed, the maximum_age parameter for Pyth price feed validation is set to 99,999 seconds (approximately 27.8 hours), which is significantly higher than recommended for secure price oracle implementations. This excessive timeout allows the use of stale price data that could be exploited during periods of high price volatility.
The issue occurs in the price validation logic where get_price_no_older_than() is called with this maximum age parameter. While the function does properly validate that the price update is not older than the specified maximum age, setting such a high threshold effectively weakens this security check.

## Recommendation
The maximum age for price feed data should be set to a more conservative value that aligns with market dynamics and security best practices. For most DeFi applications, price feeds should not be older than 5-15 minutes. Implement a more appropriate maximum age limit:
```solidity
- let maximum_age: u64 = 99999;
+ let maximum_age: u64 = 900; // 15 minutes in seconds
```
