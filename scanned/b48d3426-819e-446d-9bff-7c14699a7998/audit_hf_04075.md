# [C] ITVF-1 | Liquidations Prevented With Pending Action

## Summary
Severity: Critical
Contest weight: 0.2716
Dataset id: 20528
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
When performing a liquidation, the amount the user is to be liquidated for is validated with function
_validateWithdrawalAmountForUnwrapping:
require(balance - (withdrawalPendingAmount + depositPendingAmount) > 0);
A user can simply initiate a withdrawal for their entire balance, but specify a minOutputAmount of
long/short token that is impossible to achieve with the provided amount of GM to withdraw. If GMX
were to execute their withdrawal, the user would listen to the cancellation event, and reinitiate
another unwrapping with the same parameters.
By doing so, the user prevents the Liquidator from passing any withdrawal amount greater than 0, as
balance = withdrawalPendingAmount and balance - (withdrawalPendingAmount +
depositPendingAmount) == 0 which fails the above validation.
Furthermore, an attacker could actually perform this attack through self-liquidation, as a
minOutputAmount is passed to the prepareForLiquidation function as well.

## Recommendation
When a user attempts to initiate a deposit or withdrawal, verify whether the account is liquidatable. If
so, prevent the action from being initiated. An edge case exists such that a user may becoming
liquidatable when they already having a pending deposit/withdrawal, but this solution will prevent the
continuous, malicious use of pending deposits/withdrawals to prevent liquidation.
Furthermore, consider restricting the minOutputAmount a liquidator can pass to prevent liquidation
delay through self-liquidation.
