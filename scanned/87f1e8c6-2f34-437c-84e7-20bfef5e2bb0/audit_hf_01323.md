# [H] PHyperLPoolSwapInside::_rebalance() checks the price manipulation before and after the swap with the same price threshold

## Summary
Severity: High
Contest weight: 0.1437
Dataset id: 6529
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
PHyperLPoolSwapInside::_rebalance() checks price manipulation before swapping to prevent sandwich attacks and after swapping as a way to mitigate slippage. The same priceThreshold is used for both checks, which means that when rebalancing a large amount in comparison to the pool's liquidity, which would lead to significant slippage, an equally large priceThreshold would need to be used. This means that the PHyperLPoolSwapInside would be vulnerable to sandwich attacks.

## Recommendation
Use 2 different priceThreshold variables, the first one smaller to guarantee that no sandwich attacks will happen and a second one, which could be bigger, to check slippage.
