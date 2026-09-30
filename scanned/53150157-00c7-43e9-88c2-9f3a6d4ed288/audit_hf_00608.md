# [H] H-09 | oneRound Function Potentially Allows Negative Allocations

## Summary
Severity: High
Contest weight: 0.1376
Dataset id: 2107
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Within the oneRound function, when a negative allocation is produced by calculateXi, the inner loop is broken but the partial candidate array is still copied into bestXi. This allows negative allocations to be stored and subsequently used, totally breaking the purpose of the allocation algorithm logic. Once a negative allocation is propagated into mem.bestXi and then allocated it will corrupt the overall allocation logic, causing mismatched liquidity calculations.

## Recommendation
Update the oneRound function so bestCost and mem.bestX array are only updated if there are no negative allocations.
