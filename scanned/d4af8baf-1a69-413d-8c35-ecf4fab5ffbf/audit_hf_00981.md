# [M] Zero account value renders liquidations impossible

## Summary
Severity: Medium
Contest weight: 0.5353
Dataset id: 3066
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The liquidation process fails to handle edge cases where collateral values drop below a specified minimum (minUSDValue). This leads to a division by zero error during the assetShares calculation, rendering liquidations impossible and bad debt remaining unresolved.

When triggering a liquidation, the function computes the assetShares by calculating the relative value of each asset in relation to the totalValue of the Account.
```solidity

## Recommendation
```solidity
