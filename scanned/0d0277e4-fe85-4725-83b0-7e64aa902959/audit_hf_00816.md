# [M] M-10 | Fees Can Be Avoided With Dust Amounts

## Summary
Severity: Medium
Contest weight: 0.0849
Dataset id: 2552
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The origination fee (borrowing fee) rounds down (in favor of the borrower) and no minimum borrowing amount is enforced. Therefore borrowers can avoid paying borrowing fees by borrowing dust amounts multiple times. For example: originationFee = 0.01e18 (1%) Amount to borrow = 99 fee = amt * originationFee / 1e18 99 * 0.01e18 = 0.99e18 fee = 0.99e18 / 1e18 = 0.99 = 0 This will likely lead to a loss (because of gas fees) for the borrower on most tokens (1e18 precision) but it could be profitable with low-precision tokens.

## Recommendation
Implement a minimum borrow amount or round up (against the borrower).
