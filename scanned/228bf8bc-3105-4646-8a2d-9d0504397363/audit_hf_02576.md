# [M] No price limit in zapWETH

## Summary
Severity: Medium
Contest weight: 0.0598
Dataset id: 13905
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The zapWETH function deposits some WETH to UniV3TokenizedLp. If there is
too much WETH in UniV3TokenizedLp, some WETH will be swapped without
a price limit. Furthermore, its caller, LockZap contract, does not check
slippage. LockZap only checks the number of LPs received from the deposit.
However, this problem results in a smaller value for LPs rather than a smaller
number.

## Recommendation
Add slippage check.
