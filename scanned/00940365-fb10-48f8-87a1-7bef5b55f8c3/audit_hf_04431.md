# [M] M-03 | executionFee Should Be Updated

## Summary
Severity: Medium
Contest weight: 0.0834
Dataset id: 21907
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The createGlvWithdrawal function does not update the params.executionFee after recording the transferred wntAmount with recordTransferIn. As a consequence, users may not receive a full refund when the transferred wnt amount exceeds the provided input value. Furthermore, the validateExecutionFee function utilizes the provided params.executionFee instead of the actual transferred wnt amount, potentially causing the function to inaccurately revert even when the transferred amount is enough to cover execution costs.

## Recommendation
Update the params.executionFee after recording the transfer.
