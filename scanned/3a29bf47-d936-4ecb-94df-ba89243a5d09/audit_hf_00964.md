# [M] Missing principal fee charge in OriginationCalculator._calculateRolloverAmounts()

## Summary
Severity: Medium
Contest weight: 0.4690
Dataset id: 3027
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The repayment functions RepaymentController.repay() and RepaymentController.forceRepay() charge the feeSnapshot.lenderPrincipalFee in favor of the affiliate and the protocol. The issue is that OriginationController._rollover and RefinanceController._refinance() call OriginationCalculator._calculateRolloverAmounts() where feeSnapshot.lenderPrincipalFee is not charged.
```solidity
function _calculateRolloverAmounts(
    LoanLibrary.LoanData memory oldLoanData,
    uint256 newPrincipalAmount,
    address lender,
    address oldLender,
    IFeeController feeController
) internal view returns (OriginationLibrary.RolloverAmounts memory) {
    //...
    // Calculate amount to be sent to borrower for new loan minus rollover fees
    uint256 borrowerFee = (newPrincipalAmount * feeData.borrowerRolloverFee) /
        Constants.BASIS_POINTS_DENOMINATOR;
    // Calculate amount to be collected from the lender for new loan plus rollover fees
    uint256 interestFee = (interest * oldLoanData.feeSnapshot.lenderInterestFee) /
        Constants.BASIS_POINTS_DENOMINATOR;
    uint256 lenderFee = (newPrincipalAmount * feeData.lenderRolloverFee) /
        Constants.BASIS_POINTS_DENOMINATOR;
    // The fee `oldLoanData.feeSnapshot.lenderPrincipalFee` is not charged
    return rolloverAmounts();
}
```
This causes a loss of fees for the protocol and the old/new loan's affiliate since they don't receive Depending on the rollover fees, it could even be cheaper for borrowers to rollover their loan into a smaller one with themselves as the lender to avoid paying principal fees, rather than repaying with repay() or forceRepay().

## Recommendation
Add the principalFee and interestFee to a variable named feeFromOldLender and pass it in place of interestFee:
```diff
@@ -130,23 +130,25 @@ abstract contract OriginationCalculator is InterestCalculator {
block.timestamp
);
// Calculate amount to be sent to borrower for new loan minus rollover fees
uint256 borrowerFee = (newPrincipalAmount * feeData.borrowerRolloverFee) /
Constants.BASIS_POINTS_DENOMINATOR;
// Calculate amount to be collected from the lender for new loan plus
rollover fees
uint256 interestFee = (interest * oldLoanData.feeSnapshot.lenderInterestFee)
/ Constants.BASIS_POINTS_DENOMINATOR;
uint256 lenderFee = (newPrincipalAmount * feeData.lenderRolloverFee) /
Constants.BASIS_POINTS_DENOMINATOR;
+
uint256 principalFee = (oldLoanData.balance *
oldLoanData.feeSnapshot.lenderPrincipalFee) / Constants.BASIS_POINTS_DENOMINATOR;
+
uint256 feeFromOldLender = interestFee + principalFee;
return rolloverAmounts(
oldLoanData.terms.principal,
interest,
newPrincipalAmount,
lender,
oldLender,
borrowerFee,
lenderFee,
interestFee
+
feeFromOldLender
);
}
```
Arcade: Instead of this fix, we chose to refactor the fees and how they are assessed. There are no more ‘rollover fees’ only origination fees everywhere a loan gets started, startLoan, rollovers, migrations, refinancing... . We are not going to address the principal fee issue here since it would essentially be doubling the fee on the new principal amount. Code refactor in PR-108.
