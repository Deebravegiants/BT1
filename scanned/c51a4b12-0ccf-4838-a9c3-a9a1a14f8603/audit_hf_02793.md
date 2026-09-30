# [H] _addLiquidity() slippage is incorrectly set

## Summary
Severity: High
Contest weight: 0.5377
Dataset id: 15197
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The slippage is computed as:
```solidity
mintAmount = _args.isLegacy & 12 == 12 ?
    IPools(_args.pool).calc_token_amount(curveInputAmounts)
    : IPools(_args.pool).calc_token_amount(curveInputAmounts, true);
mintAmount = (mintAmount / 100) * 95;
```
This gets the mintAmount value post price manipulation, rendering the slippage protection useless. Also, hardcoding a parameter of 95% slippage is not ideal. Here is a similar finding.

## Recommendation
There are 2 solutions to this problem: 1. Send the minimum mint amount as argument. 2. Use an offchain oracle such as Chainlink.
