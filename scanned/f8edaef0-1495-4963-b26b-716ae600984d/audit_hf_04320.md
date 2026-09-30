# [M] M-05 | Extra Interest Charged When Extending Credit

## Summary
Severity: Medium
Contest weight: 0.0704
Dataset id: 21471
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The remediation of M-H-03 is performed via adding current day to remaining days when a user extends their credit. However, the parent finding was only causing problem when a new credit is issued with 0 added days in the last day.
Current remediation charges additional one day credit when users extend their credit regardless of when the extension is performed.

## Recommendation
Consider not allowing users to borrow more in the last day with 0 added days to fix the parent finding, rather than adding 1 day during every credit extension.
Otherwise, clearly document this behavior to users.
