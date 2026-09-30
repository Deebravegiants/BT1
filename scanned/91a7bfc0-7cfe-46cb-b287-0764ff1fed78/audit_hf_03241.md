# [H] MKTU-3 | Broken Swap

## Summary
Severity: High
Contest weight: 0.2312
Dataset id: 17860
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In the getMarkets function, the loop continues in the case of the NO_SWAP, SWAP_PNL_TOKEN_TO_COLLATERAL_TOKEN, and SWAP_COLLATERAL_TOKEN_TO_PNL_TOKEN addresses. This means that the index of these markets is left as an uninitialized Market.Props struct. Currently, when decreasing a position and swapping the collateral token to the PnL token, the first market in the swapPathMarkets is used. However according to the logic in getMarkets this market will be uninitialized. Therefore a decrease order using the shouldSwapCollateralTokenToPnlToken or the shouldSwapPnlTokenToCollateralToken feature will always revert. In the worst case, a user may make a StopLossDecrease order with either of these address variables in the swapPath expecting a swap to take place when their stop loss is hit. However the stop loss would revert upon execution, potentially leading to unintended loss of user funds, because their position is never closed.

## Recommendation
Limit these address variables to only the first index of the swapPath, and use the second item in the swapPathMarkets to perform the corresponding swap.
