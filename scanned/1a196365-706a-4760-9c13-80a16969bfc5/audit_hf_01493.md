# [M] M-4 Unsafe Math

## Summary
Severity: Medium
Contest weight: 0.0595
Dataset id: 7928
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In the project, unvalidated params with unsafe math are used. For example, it's dangerous logic
(FantiumNFTV1.sol#L620):
unchecked {
// fantiumRevenue_ is always <=25, so guaranteed to never underflow
collectionFunds = price - athleteRevenue;
}
In this case, collection.athletePrimarySalesPercentage, price, collectionId are not
validated fully.

## Recommendation
We recommend using only safe math for all operations in the project.
