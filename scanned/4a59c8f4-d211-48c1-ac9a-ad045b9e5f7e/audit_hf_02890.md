# [H] UB-2 | DoS Attack

## Summary
Severity: High
Contest weight: 0.1092
Dataset id: 16190
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
feeBettorBet is calculated based on total amount bet for a user i.e. winning side + losing side.
If the user bet more on the losing side, it is possible for the feeBettorBet to exceed the amount bet
on the winning side, causing a subtraction underﬂow which will revert. Therefore, reportResult will
consistently fail and users will not get their winnings.

## Recommendation
Calculate the fee based on the user’s bet for the winning side. Or, place a cap on the fee.
