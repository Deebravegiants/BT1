# [C] C-02 | Global Debt Is Not Changed On Debt Payment

## Summary
Severity: Critical
Contest weight: 0.1007
Dataset id: 22072
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
PerpsAccount.payDebt() updates the debt value of individual users directly instead of calling updateAccountDebt. The user's debt will be updated, but this change will not affect the global market debt and as a result reportedDebt will report higher debt.

## Recommendation
Don't update the debt directly and instead call updateAccountDebt.
