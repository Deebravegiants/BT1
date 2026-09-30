# [M] ORDH-4 | Risk-Free Trade With Disabled Feature

## Summary
Severity: Medium
Contest weight: 0.0565
Dataset id: 18209
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
If a limit order is in the dataStore and the trading features are disabled, then the possibility of a risk-free trade arises. Right before a feature is re-enabled, if prices have moved against the trader, the trader may cancel or update their limit order. Otherwise, the order can execute with outdated prices.

## Recommendation
Do not revert on the FeatureUtils.DisabledFeature error, but rather freeze or cancel these limit orders.
