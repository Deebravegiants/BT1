# [M] DPCU-5 | Liquidation Reverts Due To Underflow

## Summary
Severity: Medium
Contest weight: 0.1261
Dataset id: 18747
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Although rare, there are cases where the pendingCollateralDeduction is smaller than the fees.funding.fundingFeeAmount, resulting in a revert upon the cache.remainingCostAmount calculation in the processForceClose function. Consider the following: Position with 1 token of collateral, Fees of total 11 tokens, Funding fees of 3 tokens, Profit of 9 tokens. In this case, the profit is used to cover 9 tokens of the fees.collateralCostAmount, so the remaining fees.collateralCostAmount is 2 tokens. Therefore the values.pendingCollateralDeduction will be larger than the values.remainingCollateralAmount and the execution will enter the processForceClose function. However when the remainingCostAmount is computed, the funding fees (3 tokens) will be subtracted from the pending deduction (2 tokens) and revert.

## Recommendation
Although this scenario will be rare, the percentage of funding fees that may be covered by position profit should be accounted for to avoid an underflow.
