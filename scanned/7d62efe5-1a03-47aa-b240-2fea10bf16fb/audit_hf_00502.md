# [M] M-05 | Decreasing LP May Require Collateral

## Summary
Severity: Medium
Contest weight: 0.0954
Dataset id: 1960
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Whenever a position is modified in position.updateValidLp, the required collateral for that position is calculated and compared the current available collateral. The collateral is calculated by using two values - debitEth and creditEth (debit is taken from the user and credit is given to them). When removing a small amount of liquidity, it's possible that the decrease in creditEth is larger than the decrease in debitEth, which would lead to increased collateral requirements. Since additionalCollateral is 0 when decreasing a position, the transaction will revert with InsufficientCollateral().

## Recommendation
Allow the user to supply additional collateral when decreasing their position.
