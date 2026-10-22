# [M] SWPU-2 | Swaps Prevented When They Improve The Pool

## Summary
Severity: Medium
Contest weight: 0.0837
Dataset id: 18215
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
When performing a swap, Keys.MAX_PNL_FACTOR_FOR_WITHDRAWALS is used to check whether the current pnlToPoolFactor exceeds the maximum PnL factor for withdrawals, which is the strictest (lowest) maximum pnlToPoolFactor. When performing a swap, the tokenIn is deposited and tokenOut is withdrawn. By treating both the “deposit” and “withdrawal” with the same withdrawal pnlToPoolFactor threshold, it can potentially prevent swaps that will improve the current pnlToPoolFactor on a particular side.

## Recommendation
Consider validating tokenIn against the MAX_PNL_FACTOR_FOR_DEPOSITS and tokenOut against MAX_PNL_FACTOR_FOR_WITHDRAWALS.
