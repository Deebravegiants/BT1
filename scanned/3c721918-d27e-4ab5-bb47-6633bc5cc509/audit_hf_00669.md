# [M] M-16 | Insuﬃcient Validation In withdraw2Contract

## Summary
Severity: Medium
Contest weight: 0.0828
Dataset id: 2205
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
LedgerImplC.withdraw2Contract() doesn't implement the withdrawal validation implemented in LedgerImplA.executeWithdrawAction(). This poses a significant risk because of the withdrawNonce. Since its not validated, a lower nonce than the current last value may be used. This will then lead to overriding the last withdrawal nonce with the new value (which is way lower) and will enable past withdrawals to be executed again. The fee is also not validated which means it can exceed the maximum configured fee.

## Recommendation
Consider implementing validation for the two things mentioned in the report.
