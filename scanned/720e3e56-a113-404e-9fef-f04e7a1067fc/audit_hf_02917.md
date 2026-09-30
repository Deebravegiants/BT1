# [M] SQDF-1 | Report Result Twice

## Summary
Severity: Medium
Contest weight: 0.0464
Dataset id: 16241
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
isResultReported is not set to true after the call to reportResult. Therefore, the result can be reported multiple times with varying arguments. Furthermore, line 119 isVotingClosed = false can be used to prevent a winner from ever getting picked in pickWinner().

## Recommendation
Add isResultReported = true to the end of the function.
