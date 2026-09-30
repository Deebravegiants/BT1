# [M] deposit may not mint liquidity

## Summary
Severity: Medium
Contest weight: 0.0761
Dataset id: 13903
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The deposit function will mint liquidity only if bounds are defined. However,
the method to determine whether bounds are defined is wrong.
When baseLower and baseUpper are both 0, the bounds are undefined.
However, the deposit function does not mint liquidity as long as one of
baseLower and baseUpper is 0. For uniswap pool v3, if the price is 1, its tick
is 0. Therefore, this results in the deposit function not minting liquidity
when bounds are already defined.

## Recommendation
If one of baseLower and baseUpper is not 0, mint liquidity.
