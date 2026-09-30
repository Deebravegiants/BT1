# [M] BRT-1 | Unexpected AmountOut

## Summary
Severity: Medium
Contest weight: 0.0523
Dataset id: 4085
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Because the tradingFee is taken after the calculation of getAmountsIn, the user will receive 1000-tradingFee/10% of amountOut, rather than getting the whole amountOut. If the tradingFee is 30, the user will receive only 97% of the speciﬁed amountOut.

## Recommendation
If it is desired to receive the amountOut at minimum, take the fee in the same manner as in getAmountsIn, where the amountIn is simply increased in order to maintain the amountOut.
