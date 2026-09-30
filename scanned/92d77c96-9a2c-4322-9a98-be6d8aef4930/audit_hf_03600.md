# [H] GLOBAL-2 | USDT Treated as One Dollar

## Summary
Severity: High
Contest weight: 0.2455
Dataset id: 19579
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
During the liquidation of a position involving a different ERC-20 token, a swap occurs. In this swap, the minAmountOut is calculated to ensure a minimum amount of tokens is received. However, the estimateSellAmount function calculates the minAmountOut based on the notional value, by multiplying the amount (amount1) by the price (amount2): uint256 minAmountOut = amount1.mulDiv(amount2, 10 ** decimals); Changes in the asset's price can lead to minAmountOut being either larger or smaller than the input amount. If the price rises, the minAmountOut may exceed the input, causing the swap and liquidation attempts to fail. Conversely, if the price falls, minAmountOut may be much lower than intended, enabling swaps to exceed the intended max slippage. Other areas where USDT is assumed to be $1 is the liabilities. Because the liabilities are used in calculations such as an account’s health factor, an account may appear unhealthy when it is not and vice versa.

## Recommendation
Modify the calculation for minAmountOut in the estimateSellAmount function to be based on the expected token amount rather than the notional value. This adjustment ensures more accurate and reliable swaps during liquidation. Furthermore, use a USDT price feed to retrieve the market price.
