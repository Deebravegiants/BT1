# [C] WTDA-1 | Withdrawals With Swaps Are Incompatible

## Summary
Severity: Critical
Contest weight: 0.1047
Dataset id: 19261
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The longTokenSwapPath and the shortTokenSwapPath of a withdrawal cannot be decoded. This is because WithdrawalEventUtils.emitWithdrawalCreated does not emit the swap paths on a Withdrawal. Consequently, the withdrawal automation becomes unusable whenever a user requires a swap post-withdrawal.

## Recommendation
Add the longTokenSwapPath and shortTokenSwapPath to the WithdrawalCreated event. Afterwards, modify WithdrawalAutomation to decode these paths and _addPropsToMapping to set the necessary feeds.
