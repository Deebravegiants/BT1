# [M] Borrower can force Lender to accrue LENDER_REDEEM_FEE

## Summary
Severity: Medium
Contest weight: 0.1378
Dataset id: 3021
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The LENDER_REDEEM_FEE, which is FL_08 in FeeController.sol, is a fee incurred by the Lender whenever they use RepaymentController.redeemNote() to redeem funds that the Borrower didn't send to them directly. The issue is that the Borrower can always choose to use RepaymentController.forceRepay() to force the Lender to pay the FL_08 fee. This can be considered a form of griefing, since the Borrower can force the Lender to incur fees at no additional cost. Additionally, this fee is not stored in the loan's feeSnapshot on loan creation. As such, if the protocol increases the redemption fee during the loan's lifetime, the updated fee value will be used instead of the fee that the Lender agreed to upon loan creation.

## Recommendation
Consider removing the LENDER_REDEEM_FEE.
```diff
@@ -180,9 +180,7 @@ contract RepaymentController is IRepaymentController,
InterestCalculator, FeeLoo
address lender = lenderNote.ownerOf(loanId);
if (lender != msg.sender) revert RC_OnlyLender(lender, msg.sender);
uint256 redeemFee = (amountOwed * feeController.getLendingFee(FL_08)) /
Constants.BASIS_POINTS_DENOMINATOR;
loanCore.redeemNote(loanId, redeemFee, to);
+
loanCore.redeemNote(loanId, 0, to);
}
```
Otherwise, include the redemption fee in feeSnapshot, which ensures that the redemption fee was agreed upon by the lender on loan creation.
