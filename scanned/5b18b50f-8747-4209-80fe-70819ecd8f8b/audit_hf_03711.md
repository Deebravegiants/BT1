# [H] No slippage for withdrawal without swap

## Summary
Severity: High
Contest weight: 0.2827
Dataset id: 19822
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
No slippage for withdrawal without swapping path. When user withdraws, he should provide amount of LP tokens, that he wants to burn. According to that amount, output amount of long and short tokens of the market will be calculated for him.

In case if user wants to swap this short/long tokens to another tokens, then he can provide longTokenSwapPath/shortTokenSwapPath array. If he doesn't want to swap them, but just receive without swapping, he doesn't provide that array. No matter if he provided swap path or no, swapping will be called.

Then inside SwapUtils.swap in case if no swap path is provided, then function will just send tokens to receiver. One of parameters of SwapUtils.swap function is minOutputAmount. This parameter is important as it stands as slippage protection. In case if swap path is not provided, then amount will not be checked for that slippage. If swap path present, then slippage check will be done. So in case if no swap path is provided, then slippage provided by user will not be checked, as inside WithdrawalUtils._executeWithdrawal there is no any check that user received minShortTokenAmount and minLongTokenAmount. Because of that user can be frontrunned and lose some funds. There is no slippage check in case if user doesn't provide swap path.

## Recommendation
You need to check that minLongTokenAmount, minShortTokenAmount is satisfied after the swap.
