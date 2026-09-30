# [C] DPU-6 | No Market Validation When Swapping Collateral to PnL

## Summary
Severity: Critical
Contest weight: 0.1563
Dataset id: 17852
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Because the swapPath is simply the first element of the swapPathMarket, a malicious user could supply an arbitrary market which contains the collateral token. Such a market does not need to contain the PnL token, even though the purpose of the swap is to get the PnL token from collateral token. With the current logic, this can be used to inflate the values.outputAmount as per DPU-5. If the logic was amended so that the cache.outputToken was the pnlToken, the amount of pnlToken to withdraw from the market can be inflated.

## Recommendation
Add validation such that the market in the swapPathMarkets actually contains both the collateral token and PnL token, and that the token received from the swap is indeed the PnL token.
