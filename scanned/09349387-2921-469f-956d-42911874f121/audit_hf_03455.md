# [M] DPCU-3 | Collateral Prioritized Over PnL

## Summary
Severity: Medium
Contest weight: 0.0816
Dataset id: 18865
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In the payForCost function, the collateral token is prioritized over the secondary token when making payments. As a result, a user’s collateral could be unexpectedly reduced when their is substantial PnL or price impact in the secondary token available to cover the cost. This can be especially unexpected for costs such as negative price impact which would commonly be thought of as affecting the execution price and being deducted from the PnL.

## Recommendation
Consider prioritizing secondary token amounts over collateral when paying amounts such as negative price impact. Otherwise, document that the user’s collateral will be prioritized over secondary PnL.
