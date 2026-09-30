# [M] UF-5 | Price Inconsistency

## Summary
Severity: Medium
Contest weight: 0.0517
Dataset id: 16219
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In the getPrice function the stepwise price jumps do not account for the following tokenIds: 101, 301, 601, 1001, 1501, and 2301. This is because each if statement utilizes > instead of >= when referring to these tokenIds. Therefore a mint for one of these tokenIds will mistakenly go to the else branch and charge 6 FTM.

## Recommendation
Use >= or decrement the lower boundaries by one.
