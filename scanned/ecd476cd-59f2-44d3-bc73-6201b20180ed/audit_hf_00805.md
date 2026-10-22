# [M] M-06 | Repay & Seize Order Increases Bad Debt Risk

## Summary
Severity: Medium
Contest weight: 0.0790
Dataset id: 2541
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In the current liquidate flow the liquidator has to first repay debt from the own pocket and receive funds from the liquidated borrower's position after that. If the unhealthy position is very big, fewer users (or no one) might be able to repay it from their own wallet.
Reversing the order of this flow (seize before repay) could enable more users to have enough funds to repay the debt. This leads to more liquidations on time and therefore decreases the likelihood of bad debt.

## Recommendation
Reverse the order of the repay and seize loop in the liquidate function.
