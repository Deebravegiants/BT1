# [C] C-06 | Users Can Withdraw Their Collateral Without Paying Debt

## Summary
Severity: Critical
Contest weight: 0.1840
Dataset id: 21111
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Users without sUSD deposited as collateral will accumulate losses in debtUsd. This happens in
updateAccountDebtAndCollateral. In the scenario where a trader closes a position, and realizes a
loss, there will be some collateral left and a pending debtUsd to pay.
The issue arises when a user tries to withdraw the deposited collateral without any open position.
The validatePositionPostWithdraw will fail to do its job, as the position.size is 0, leading to
isLiquidateable to return false and im to be 0. Therefore, the protocol will allow users to withdraw all
their collateral, even with a pending debt to pay.

## Recommendation
Validate the case where there is no open position, checking if the discountedCollateralUsd <
debtUsd.
