# [M] GSU-3 | No Way For Users To Claim Excess Execution Fee

## Summary
Severity: Medium
Contest weight: 0.0521
Dataset id: 18213
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
handleExcessExecutionFee does not allow users to claim the excess executionFee that they may have sent. Currently the excess is simply sent to a holding address with no accounting of which user is in excess or by how much and there is no way to claim the excess fee.

## Recommendation
Either make a way for users to claim these tokens or ensure it is well documented and explicit that these tokens will be lost for the user.
