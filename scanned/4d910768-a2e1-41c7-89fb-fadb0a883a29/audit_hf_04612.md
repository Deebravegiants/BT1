# [M] M-11 | Inflated Admin Fee

## Summary
Severity: Medium
Contest weight: 0.0840
Dataset id: 22217
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
When a swap fails in depositFromPairedLPToken(), the amount that can be used in the next attempt is halved from the attempted swap amount. The next time depositFromPairedLPToken() is called the fee will be based off the current balance of the contract, which will include the balance from the failed swap. When _swapForRewards is called, it will reduce the _amountIn and _amountOut but still charge the admin fee based on the balance of the contract. This results in excessive admin fees paid over the multiple swaps.

## Recommendation
Adjust the admin fee to match the actual amount that has been swapped.
