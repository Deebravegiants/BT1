# [H] UniswapV2Swapper uses block.timestamp for deadline [Out of scope]

## Summary
Severity: High
Contest weight: 0.0808
Dataset id: 8209
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Uniswap sets a deadline to limit arbitrage opportunities if the swap does not get included right away. If the swap specifies a deadline of block.timestamp, then the swap transaction can be included in any block. This means that the price can, by then, have changed significantly.

## Recommendation
Send a deadline argument.
