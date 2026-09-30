# [M] M-03 | setPrices Function Does Not Accurately Retrieve The Asset Prices

## Summary
Severity: Medium
Contest weight: 0.1561
Dataset id: 2127
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The protocol’s current configuration for the oracle-driven pricing mechanism allows the price expiration to be set anywhere between 30 seconds and up to 24 hours which. As a result, when a broker performs a multicall that begins with calling setPrices to load price data and then proceeds to fill position orders, liquidity orders etc. the entirety of these operations may rely on prices that belong to different timestamps from the range: [block.timestamp - 24 hours, block.timestamp]. Traders can use multiple collateral tokens to maintain their positions. Let’s imagine that a trader holds a position backed by USDC, WETH and WBTC and the oracleIds for these assets have an expiration time of 24 hours and are using Chainlink Price Feeds with a heartbeat of 86400 seconds. When the broker calls setPrices the price received for USDC could be from second 86399, for WETH 40000 and for WBTC 1. Therefore, this could result in positions that might be incorrectly assessed as safe or unsafe leading to unfair liquidations, missed opportunities for profitable trades…

## Recommendation
Consider integrating with low-latency, high-frequency oracle solutions like Pyth, which provide more up-to-date prices with tighter heartbeat intervals.
