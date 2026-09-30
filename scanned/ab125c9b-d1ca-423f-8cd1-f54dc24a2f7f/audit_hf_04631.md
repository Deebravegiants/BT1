# [H] Calculation for `directionMask` is incorrect

## Summary
Severity: High
Contest weight: 0.0930
Dataset id: 22324
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The `_getQuoteAndDirection` function’s flawed logic can cause incorrect direction determination in the UniswapV3 pool. The recommended mitigation ensures that the function dynamically identifies token0 and token1 and assigns the correct direction mask. This prevents potential financial losses and ensures accurate rebalancing.

## Recommendation
No recommendation
