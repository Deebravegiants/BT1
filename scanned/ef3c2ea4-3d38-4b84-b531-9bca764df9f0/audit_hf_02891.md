# [H] UB-3 | Lost Funds On Cancel

## Summary
Severity: High
Contest weight: 0.0857
Dataset id: 16191
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The contract allows placing bets on both sides which makes sense if the user would like to perform
arbitrage. If the event is canceled upon an emergency, a user can only withdraw funds from one side.
If they were betting on both sides for arbitrage, they lose the amount they bet on the other side.

## Recommendation
Don’t set both sides of a user’s bet to 0.
