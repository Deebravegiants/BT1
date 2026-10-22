# [M] M-04 | Zero Platform Fee Can DoS New Loans

## Summary
Severity: Medium
Contest weight: 0.0700
Dataset id: 20865
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In the setLoanOriginationFee function there is not validation that the _loanOriginationFee is not 0, therefore the platformFee that is taken from new loans can be 0 when the loanOriginationFee is set to 0. Some ERC20 tokens choose to revert upon transferring a 0 amount, however there is no check that the platformFee is nonzero before attempting to transfer this amount to the platformWallet.

## Recommendation
In the initializeNewLoan function, only attempt to transfer the platformFee to the platformWallet if the platformFee is nonzero.
