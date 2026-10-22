# [H] DIEM-5 | mulDivUp Leads To Unliquidatable Position

## Summary
Severity: High
Contest weight: 0.1999
Dataset id: 90
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In the _closeTrade function mulDivUp is used to compute the borrowed amount to be subtracted from the utilized collateral. In some cases, when a trade is closed in multiple transactions the resulting decrease of the utilized collateral will be greater than the corresponding increase that opening that trade incurred. Therefore in some cases the computed borrowedAmount to decrease may be greater than the current utilizedCollateral amount. When the computed borrowedAmount is greater than the utilizedCollateral in the IVXLP contract, the transaction will underflow revert and prevent the position from being closed. Malicious actors can leverage this to halt liquidations and grief other users, preventing positions from being closed.

## Recommendation
Refactor the subUtilizedCollateral function such that if the provided _amount value is greater than the existing utilizedCollateral the function does not revert but instead assigns the utilizedCollateral to 0.
