# [M] Incorrect refund of execution fee to

## Summary
Severity: Medium
Contest weight: 0.2664
Dataset id: 19833
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
During execution of Deposits, Withdrawals and Orders, users are refunded part of
the executionFee after accounting for gasUsed during the transaction. In the
codebase, an incorrect value of startingGas is used to calculate the gasUsed,
resulting in users getting less than what they should be refunded.
Vulnerability exists in DepositHandler.sol, WithdrawalHandler.sol and
OrderHandler.sol. Using DepositHandler.sol as an example:
https://user-images.githubusercontent.com/83704326/227539224-f59d4cb7-f638-4ddd-a7b3-794
(1) In line 94 of DepositHandler.sol, Order Keepers call executeDeposit() and
startingGas is forwarded to an external call _executeDeposit. (2) In
ExecuteDepositUtils.sol, _executeDeposit further calls
GasUtils.payExecutionFee(... params.startingGas. (3) Then in GasUtils.sol,
payExecutionFee() calculates gasUsed = startingGas - gasleft(); (4) gasUsed is
used to calculate executionFeeForKeeper, and after paying the fee to keeper, the
remainder of executionFee (previously paid by user) is refunded to the user
The issue lies with (1) where startingGas is passed into _executeDeposit and
assumed to be all remaining gas left. EIP-150 defines the "all but one 64th" rule,
which states that always at least 1/64 of the gas still not used for this transaction
cannot be sent along. Therefore, in (3) gasUsed is overstated by 1/64 and the refund
back to user in (4) is incorrect (less than what user should get back).
GMX Users will receive an incorrect refund from the execution fee and will be
overpaying for deposit, withdraw and order executions.

## Proof of Concept
https://user.googleapis.com/download/storage/v1/b/user-content/o/83704326%2F227538387-f2f2ca87-d&generation=1679615800000000&alt=media
In the test above, it is demonstrated that external function calls are forwarded with
only 63/64 of the remaining gas. A separate internal function call used to
demonstrate the difference in gas costs.

## Recommendation
In DepositHandler.sol, for executeDeposit it is recommended that startingGas() is
calculated after the external call is made.
https://user-images.githubusercontent.com/8370432
Alternatively, in GasUtils.sol, gasUsed could be computed with 63/64 of
startingGas, in order to obtain the correct refund amount to the user. This would
also apply to Withdraw and Order executions which have similar code flows.
https://user-images.githubusercontent.com/83704326/227539740-4df5497a-709d-4e4c-ad00-ab4
