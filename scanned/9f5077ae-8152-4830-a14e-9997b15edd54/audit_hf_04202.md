# [C] C-09 | debtCorrection Not Updated Upon Realizing To Account Margin

## Summary
Severity: Critical
Contest weight: 0.1536
Dataset id: 21095
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In the mergeAccounts function the outstanding PnL for the to account is realized, however the
debtCorrection is not updated to account for this realized PnL.
As a result every merge where the to account has outstanding PnL will result in a double counting of
that PnL in the debtCorrection, as the skew still includes the old position and the account has now
materialized it’s gain or loss into it’s collateral.

## Proof of Concept
https://docs.google.com/spreadsheets/d/12CWdeXT8OQ4BtpM2L-xrldF6W45i2mE4QrpenAujlho/edit?usp=sharing

## Recommendation
Update the debtCorrection for the settlement of the to account’s PnL.
