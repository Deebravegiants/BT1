# [H] H-02 | cancelDeposit Missing totalDepositAmt Deduction

## Summary
Severity: High
Contest weight: 0.1994
Dataset id: 21942
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The cancelDeposit function allows the protocol to cancel an ongoing deposit, resetting the state and
deleting the deposit request.
However, it currently forgets to deduct the deposit request's amount from the totalDepositAmount
state variable. This variable is used to ensure that the deposited amount within the protocol remains
under the deposit cap.
Consequently, the missing deduction in the cancelDeposit function will lead to an overestimation of
the total deposits. Every time cancelDeposit is called, the remaining possible deposit amount
(maxDepositAmount - totalDepositAmount) will be incorrectly reduced by the cancelled amount.
This will incorrectly limit deposits, affecting the vault strategy and, in the worst case, could cause a
DOS for the entire vault.

## Recommendation
Ensure that the cancelDeposit function deducts the cancelled deposits amount from the
totalDepositAmount state variable.
