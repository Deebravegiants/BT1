# [M] EDPU-1 | Positive Impact Deposit Not Validated

## Summary
Severity: Medium
Contest weight: 0.0561
Dataset id: 19223
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In the _executeDeposit function the pool amount is incremented by the positive price impact amount
in the _params.tokenOut.
However only the _params.tokenIn is validated against the validatePoolAmountForDeposit
validation. This could lead to the tokenOut balance exceeding the desired cap during deposits.

## Recommendation
Validate that the increased tokenOut amount is also within the deposit cap with
validatePoolAmountForDeposit.
