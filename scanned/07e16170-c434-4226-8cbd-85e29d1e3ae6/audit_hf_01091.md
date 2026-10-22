# [M] Fee-on-transfer token compatibility Issue in protocol Burve::mint

## Summary
Severity: Medium
Contest weight: 0.0694
Dataset id: 4174
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The Burve::mint function interacts with the uniswapV3MintCallback, which transfers token0 and token1 to the Uniswap pool. However, fee-on-transfer tokens (tokens that deduct a percentage as a fee on each transfer) are not properly accounted for in this implementation.
When using fee-on-transfer tokens, the amount received by the pool will be less than the expected amount, causing the minting process to fail due to an arithmetic underflow.

## Recommendation
No data
