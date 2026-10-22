# [M] RH-5 | Not Subtracting Full Size On Withdrawal

## Summary
Severity: Medium
Contest weight: 0.5645
Dataset id: 20518
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
epochDelta is used to track the amount of deposits/withdrawals during an epoch. It grows positive when more funds are being deposited than being withdrawn and vice versa.

The issue arises due to how the protocol increments and decrements epochDelta. The protocol increments the delta with the amount deposited after the fees get subtracted from it, thus only incrementing with the amount that entered the AggregateVault.
```solidity
aggregateVault.incrementEpochDelta(underlyingToken, assetsSansFees.toInt256())
```
However, the same pattern is not followed in the withdrawal logic. Instead of decreasing the whole amount that leaves the vault only size - fees get subtracted.
```solidity
aggregateVault.incrementEpochDelta(underlyingToken, -(assetsSansFees.toInt256()))
```
This will result in an imbalance where depositing the same amount has a higher impact on increasing epochDelta compared to the mitigating effect of withdrawing, thereby exposing the protocol to fund loss due to reduced fees.

This happens due to the subtraction of positive epochDelta from the current TVL during withdrawal fee calculations.

## Recommendation
Decrement epochDelta by assets instead of assetsSansFees.
