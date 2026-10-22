# [H] H-03 | Restructure Debt Locks Up Funds

## Summary
Severity: High
Contest weight: 0.1452
Dataset id: 2155
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
When a position’s debt is restructured, the debt is forgiven, the losses socialized, and the position remains in the system. In certain cases, the position can become liquidatable after restructuring and be liquidated, and other times the position can become fully healthy and remain. This incongruent behavior may be unexpected for the protocol, since some positions will effectively get a bail-out and remain. This can be used by malicious borrower’s to keep lender’s funds locked up indefinitely.

## Recommendation
Consider if previously underwater positions should remain in the system after restructuring and allow them to be liquidated.
