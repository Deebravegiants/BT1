# [M] M-1 Incorrect usage of the parameter

## Summary
Severity: Medium
Contest weight: 0.0489
Dataset id: 2897
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
There are not enough checks on the amount of liquidity that can be removed from the limit order in the decreaseLimitOrder function. liquidity can be greater than the available liquidity on the limit order and in this case tx will revert. LimitOrderManager.sol#L162

## Recommendation
We recommend decreasing liquidity to cache.liquidityLast if liquidity > cache.liquidityLast.
