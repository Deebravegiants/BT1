# [H] `Lender` does not handle correctly rebasing, inflationary, deflationary tokens and tokens with fee on transfer

## Summary
Severity: High
Contest weight: 0.2376
Dataset id: 3690
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The current implementation of the Lender contract does not handle these kinds of tokens:
Rebasing tokens
Inflationary tokens
Deflationary tokens
Tokens with fee-on-transfer

The accounting variables on the Loan and Pool structs will store an incorrect value that could lead to reverts or further accounting errors.

The current implementation of the Lender contract does not handle these kinds of tokens:
Rebasing tokens
Inflationary tokens
Deflationary tokens
Tokens with fee-on-transfer

The accounting variables on the Loan and Pool structs will store an incorrect value that could lead to reverts or further accounting errors.

All the following accounting variables will store the incorrect amount of tokens:
loan.debt
loan.collateral
pool.poolBalance
pool.outstandingLoans

The accounting variables on the Loan and Pool structs will store an incorrect value that could lead to reverts or further accounting errors.

## Recommendation
The protocol should choose one of the following options:

1) Have a list of whitelisted collateral and lending tokens that can be used
2) Correctly account the real amount that has been deposited to the Lender contract or from the Lender contract after the transfer has happened
