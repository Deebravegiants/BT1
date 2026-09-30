# [M] ML-3 | User Loses More Collateral Than Necessary

## Summary
Severity: Medium
Contest weight: 0.1311
Dataset id: 19559
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
During a liquidation, the total amount to be liquidated and the amount of supply to withdraw from the user’s portfolio to the Liquidator is calculated in function calculateLiquidation() With those parameters the liquidation is settled in function settleLiquidation(), where the total amount being repaid is adjusted to be no more than the user’s liabilities: uint256 repayAmount = Math.min(context.totalAmount, context.liabilities); Consequently, the amount to repay can be dramatically decreased yet the amount withdrawn from the user's supply is still the originally calculated supply. Although the the excess of the user’s liabilities is refunded, the supply was valued at the discounted price so the user has more supply withdrawn from their portfolio than necessary. This results in an extra “liquidation fee” causing loss of funds for users.

## Recommendation
Consider adjusting context.position by the discounted price to accurately reflect the amount being repaid. Otherwise, clearly document this behavior to users.
