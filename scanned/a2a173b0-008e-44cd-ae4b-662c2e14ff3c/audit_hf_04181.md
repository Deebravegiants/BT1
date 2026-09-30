# [M] M-01 | Overlap Between Payment And Default Periods

## Summary
Severity: Medium
Contest weight: 0.0564
Dataset id: 20862
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Since the hoursElapsed is rounded down in the getLoanAmountDue function and the loan.duration check uses strictly greater than, loan payments are only disabled an entire hour after the end date of a loan. Therefore during this time a borrower may still pay back their loans and may frontrun the liquidation tx to do so.

## Recommendation
Alter the hoursElapsed > loan.duration check to be hoursElapsed >= loan.duration
