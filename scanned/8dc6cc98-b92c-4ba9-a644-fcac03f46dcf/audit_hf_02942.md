# [H] leading to loss of funds

## Summary
Severity: High
Contest weight: 0.1597
Dataset id: 16293
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
state.cumulativeDepositsMultiplierX18 may go below 0 if an account is socialized or in the worst case, 0, which will have greater impact. The point of socializing a spot account is eliminating the borrowed amount from the short account and transferring it to the other depositors. The problem is that the multiplier may become 0 or negative which is never handled. If the multiplier goes to 0, every deposit will revert and the user will lose its funds. If it becomes negative, every deposit will be treated as a short instead and the user may be liquidated (deposits have no health check).

## Recommendation
Don't let the multiplier become 0 or lower by reverting in this case.
