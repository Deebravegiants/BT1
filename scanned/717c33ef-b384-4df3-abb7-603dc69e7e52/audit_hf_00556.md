# [H] H-01 | Match Withdrawal Donation Underflow

## Summary
Severity: High
Contest weight: 0.1306
Dataset id: 2016
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In the matchWithdrawRequest the donation amount is not deducted from the withdrawal request
when the transaction is a partial withdrawal fill.
In this case the donation amount can be larger than the remaining amount for the withdrawal
request and lead to an underflow panic revert on the subsequent withdrawal match. This prevents
the user’s withdrawal request from being filled after this case has been reached.

## Recommendation
Consider refactoring the withdrawal donation computation by using a ratio of the request.donation
to the original entire withdrawal request amount to compute the donationPart.
