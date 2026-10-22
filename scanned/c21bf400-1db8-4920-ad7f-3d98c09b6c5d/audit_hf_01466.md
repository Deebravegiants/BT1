# [M] M-1 Absence of Fee-on-transfer Protection in _deposit Function

## Summary
Severity: Medium
Contest weight: 0.1337
Dataset id: 7669
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
An oversight has been detected within the _deposit function of the EnjoyoorsVaultDeposits contract.
The issue arises from the absence of a fee-on-transfer protection mechanism. This could result in incorrect
setting of user amounts. Consequently, users might be in a position to claim more than they are entitled to. It
gravely threatens the contract's integrity since this scenario inevitably leads to a situation where the last user
cannot claim any funds, given there are insufficient funds on the contract due to the over-claims made by the
preceding users.
This issue is classified as Medium severity due to its potential to distort the distribution of deposits and
consequently funds, which could lead to the breakdown of the contract's operation.

## Recommendation
We strongly suggest the addition of a fee-on-transfer protection within the _deposit function. This would
ensure the correct amount is allocated to the user upon executing a deposit transaction, especially for tokens
with transfer fees. This can be done by adding balance checks for the token before and after the
transferFrom call. Note that it is crucial to add a nonReentrant check to protect the function from the
reentrancy attack.
