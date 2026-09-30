# [C] C-01 | User Debt Overwritten When Cancelling Orders

## Summary
Severity: Critical
Contest weight: 0.1424
Dataset id: 21106
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
When canceling an order with the cancelOrder function the keeper fee is directly accounted with
updateAccountDebtAndCollateral, however if the user has no sUSD collateral
updateAccountDebtAndCollateral reassigns the account’s debt to the keeper fee, therefore
overwriting any existing debt for the account.

## Proof of Concept
https://github.com/GuardianAudits/synthetix-pocs-2/commit/bf54c77b7bdaa66efeb8a77007c626a58c061771

## Recommendation
Consider Including the accounts existing debt when charging the fee with the
updateAccountDebtAndCollateral function, otherwise create a dedicated function to charge the
keeper fee from the user’s margin.
