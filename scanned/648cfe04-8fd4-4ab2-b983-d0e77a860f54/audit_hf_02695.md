# [C] amountOut Not Converted to shares

## Summary
Severity: Critical
Contest weight: 0.2566
Dataset id: 14579
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Function swap() swaps amountIn of tokenIn to amountOut of tokenOut. To calculate amountIn, this function deducts the current balances (balance0 and balance1) with the previous recorded balances (stored in variable reserve0 and reserve1). According to internal functions _getReservesAndBalances() and _balance(), all of these values (balance0, balance1, reserve0, and reserve1) are expressed in BentoBox’s amount (or elastic). This means, amountIn is also in amount.
The function swap() further uses amountIn to calculate amountOut through internal function _getAmountOut(). It is safe to assume that amountOut is also in amount, because there is no amount-shares conversion in the _getAmountOut() function.
The problem is that amountOut is used in function _transfer() that requires shares and not amount. This means that the user may receive more tokens than expected, especially in cases where BentoBox receives significant profits from its strategy contracts.
Function getAmountOut() shows the correct process, where the outcome of function _getAmountOut() is converted to share to get finalAmountOut.

## Recommendation
The testing team recommends converting amountOut to shares before transferring tokens through function _transfer().
