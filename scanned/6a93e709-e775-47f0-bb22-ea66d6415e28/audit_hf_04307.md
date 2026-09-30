# [H] H-04 | Leverage And Deleverage Are Sandwichable

## Summary
Severity: High
Contest weight: 0.1592
Dataset id: 21457
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In the leverage and deleverage functions traders flash borrow and repay using a swap where the maxAmountIn is the borrowed amount for borrows and the unlocked collateral amount for repayments.
This allows malicious actors to frontrun these actions and push the price far enough such that these limits are hit. In the case of borrowing, this leaves the borrower with no funds received from the action as the reservesNeeded can be pushed to the maximum of the entire newPrincipal_.

## Recommendation
Allow the user to configure an amountInMaximum themselves, and do not allow this amountInMaximum to be greater than the borrowed amount for borrows and the unlocked collateral amount for repayments.
Additionally, consider allowing the user to configure the sqrtPriceLimitX96 and deadline on the swap for additional MEV protection.
