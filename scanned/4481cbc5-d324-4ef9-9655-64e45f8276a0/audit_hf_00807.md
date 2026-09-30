# [M] M-08 | Bad Debt Is Not Handled

## Summary
Severity: Medium
Contest weight: 0.0817
Dataset id: 2543
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
At the moment the system does not handle bad debt, the liquidator always has to repay the full loan.
If the loan to repay is higher than the assets in the Position it makes no economic sense to call liquidate as the liquidator would lose money. This leads to no one calling liquidate if bad debt occurs and the bad debt probably increases even further.
The missing opportunity to take bad debt would lead to major problems in the system when a black swan event occurs.

## Recommendation
Handle bad debt by repaying the maximum amount possible and either reducing the amount owned by the lenders or increasing the debt of the borrowers.
