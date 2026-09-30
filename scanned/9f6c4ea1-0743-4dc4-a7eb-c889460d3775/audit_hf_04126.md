# [M] ISU-6 | Users Can Avoid Withdrawal Fee

## Summary
Severity: Medium
Contest weight: 0.0980
Dataset id: 20586
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
When a user submits a withdrawal, either through direct assets or through EigenLayer, a fee is deducted. When using the Issuance contract, users have the possibility to complete other's withdraws by paying the due value and changing ownership of the pending withdrawal. This mechanism, however, does not deduct any fees from the new owner, this results in: Disincentivizing anyone from initiating a direct withdrawal from EigenLayer and simply waiting for others to initiate the withdraw and changing it, so that they may not pay the fee The protocol does not receive fees for withdrawal done in this manner

## Recommendation
Deduct the withdraw fee also on the Issuance contract when doing an completeWithdrawEarly function call.
