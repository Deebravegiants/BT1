# [H] Use unchecked in TickMath.sol and FullMath.sol

## Summary
Severity: High
Contest weight: 0.1247
Dataset id: 11198
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Uniswap math libraries rely on wrapping behaviour for conducting arithmetic operations. Solidity version 0.8.0 introduced checked arithmetic by default where operations that cause an overflow would revert. Since the code was adapted from Uniswap and written in Solidity version 0.7.6, these arithmetic operations should be wrapped in an unchecked block.

## Recommendation
Add an unchecked block to the following functions in TickMath.sol and FullMath.sol:
• getSqrtRatioAtTick()
• getTickAtSqrtRatio()
• mulDiv()
• mulDivRoundingUp()
The Uniswap protocol has a reference implementation for these changes in a branch named 0.8.
