# [M] M-02 | Failed Approvals With USDT

## Summary
Severity: Medium
Contest weight: 0.0673
Dataset id: 2171
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Function repay approves amount and then calls SparkLend to repay the amount. The issue is that the paybackAmount within the BorrowLogic is not necessarily equal to amount passed, so a portion of the approved amount will be not be utilized. This will lead to DoS with tokens such as USDT which require a 0 approval initially.

## Recommendation
For all allowances in K33, use SafeERC20's forceApprove which will force the allowance to go to zero initially to handle tokens such as USDT. Also, use it after an external call to set the approval to zero after the approval is no longer necessary.
