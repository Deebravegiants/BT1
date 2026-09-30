# [M] M-05 | Discovery Liquidity Increased Above MAX_DISCOVERY_RATIO

## Summary
Severity: Medium
Contest weight: 0.1259
Dataset id: 21485
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The ratio between the DISCOVERY and ANCHOR liquidity during a sweep operation should be capped by the MAX_DISCOVERY_RATIO (5x), following this logic: liquidityPremium = (liquidityPremium / liquidityA) > MAX_DISCOVERY_RATIO ? liquidityA * MAX_DISCOVERY_RATIO : liquidityPremium; The issue relies on the ratio liquidityPremium / liquidityA, as this division rounds down in Solidity. Therefore, every time this division rounds down to the value of MAX_DISCOVERY_RATIO (5), then liquidityPremium value is not updated, due to the > comparison. Because liquidityPremium on its own is larger than liquidityA * MAX_DISCOVERY_RATIO, this rounding issue allows the DISCOVERY liquidity to increase up to almost 7x the ANCHOR liquidity during sweep rebalancing.

## Recommendation
Consider updating the comparison to include ratios equal to MAX_DISCOVERY_RATIO: liquidityPremium = (liquidityPremium / liquidityA) >= MAX_DISCOVERY_RATIO ? liquidityA * MAX_DISCOVERY_RATIO : liquidityPremium; This prevents liquidityPremium / liquidityA ratio to end up being greater than 6x.
