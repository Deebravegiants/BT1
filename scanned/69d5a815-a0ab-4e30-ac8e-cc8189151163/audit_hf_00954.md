# [M] Permanent DOS of OriginationControllerMigrate.migrateV3Loan() after the first migration

## Summary
Severity: Medium
Contest weight: 0.6188
Dataset id: 3011
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
During OriginationControllerMigrate.migrateV3Loan(), a call is made to OriginationControllerMigrate.rolloverAmounts() to calculate the OriginationLibrary.RolloverAmounts needed for the migration.

OriginationControllerMigrate.rolloverAmounts() includes the lenderFee and borrowerFee inside amounts.amountFromLender and amounts.needFromBorrower.

This becomes an issue when later the repayAmount passed as a parameter to OriginationControllerMigrate_repayLoan() is calculated with the values that include the fees.

```solidity
_repayLoan(msg.sender, IERC20(newTerms.payableCurrency), oldLoanId,
    amounts.amountFromLender + amounts.needFromBorrower - amounts.amountToBorrower);
```

Later in OriginationControllerMigrate_repayLoan() we have the line:

```solidity
// approve LoanCoreV3 to take the total settled amount
payableCurrency.safeApprove(loanCoreV3, repayAmount);
// repay V3 loan, this contract receives the collateral
IRepaymentControllerV3(repaymentControllerV3).repay(borrowerNoteId);
```

The repayment mechanism in V3 will pull from OriginationControllerMigrate only the owed principal + interest, therefore, because the approved amount included the borrower and lender “origination” fees, OriginationControllerMigrate will have a > 0 approval left towards V3.

This will make migrations for the particular payableCurrency impossible since on the next attempt to migrate, payableCurrency.safeApprove(loanCoreV3, repayAmount) will revert with SafeERC20: approve from non-zero to non-zero allowance.

For example:
- Borrower owes $100 + $20 interest to Lender 1 in V3
- Assume $5 per origination fee in V4
- Borrwer migrates with Lender 2 for the same $100 principal
- borrowerOwedForNewLoan = $100 - $5 = $95
- amounts.amountFromLender = $100 + $5 = $105
- repayAmount = $100 + $20 = $120
- amounts.needFromBorrower = $120 - $95 = $25
- in _repayLoan(), repayAmount = amounts.amountFromLender + amounts.needFromBorrower
- repayAmount = $105 + $25 = $130
- _repayLoan() approves $130 to V3
- V3 pulls $120 (principal + interest)
- excess approval = $10
- Future calls to migrateV3Loan() are not possible since safeApprove() reverts with “SafeERC20: approve from non-zero to non-zero allowance”

## Recommendation
The suggested fix is to calculate the repayment amount for the V3 loan using the oldTerms when the old loan's interest amount is fetched in OriginationControllerMigrate._calculateV3MigrationAmounts().

Then, the calculated repay amount will be returned upwards to OriginationControllerMigrate.migrateV3Loan() and passed over to OriginationControllerMigrate._initiateFlashLoan() or OriginationControllerMigrate._repayLoan().

```diff
@@ -103,14 +103,15 @@ contract OriginationControllerMigrate is IMigrationBase,
OriginationController,
// collect and distribute settled amounts
(
    OriginationLibrary.RolloverAmounts memory amounts,
    bool flashLoanTrigger
+
    bool flashLoanTrigger,
+
    uint256 repayAmount
) = _migrate(oldLoanId, oldLoanData, newTerms.principal, msg.sender, lender);
// repay v3 loan
if (flashLoanTrigger) {
    _initiateFlashLoan(oldLoanId, newTerms, msg.sender, lender, amounts);
+
    _initiateFlashLoan(oldLoanId, newTerms, msg.sender, lender, amounts, repayAmount);
} else {
    _repayLoan(msg.sender, IERC20(newTerms.payableCurrency), oldLoanId,
        amounts.amountFromLender + amounts.needFromBorrower - amounts.amountToBorrower);
+
    _repayLoan(msg.sender, IERC20(newTerms.payableCurrency), oldLoanId, repayAmount);
    if (amounts.amountToBorrower > 0) {
        // If new principal is greater than old loan repayment amount, send the difference to the borrower
@@ -204,7 +205,8 @@ contract OriginationControllerMigrate is IMigrationBase,
OriginationController,
address lender
) internal nonReentrant returns (
    OriginationLibrary.RolloverAmounts memory amounts,
    bool flashLoanTrigger
+
    bool flashLoanTrigger,
+
    uint256 repayAmount
) {
    address oldLender = ILoanCoreV3(loanCoreV3).lenderNote().ownerOf(oldLoanId);
    IERC20 payableCurrency = IERC20(oldLoanData.terms.payableCurrency);
@@ -213,7 +215,7 @@ contract OriginationControllerMigrate is IMigrationBase,
OriginationController,
(, uint256 borrowerFee, uint256 lenderFee) = feeController.getOriginationFeeAmounts(newPrincipalAmount);
// Calculate settle amounts
(amounts) = _calculateV3MigrationAmounts(
+
(amounts, repayAmount) = _calculateV3MigrationAmounts(
    oldLoanData,
    newPrincipalAmount,
    lender,
@@ -260,13 +262,16 @@ contract OriginationControllerMigrate is IMigrationBase,
OriginationController,
address oldLender,
uint256 borrowerFee,
uint256 lenderFee
) internal view returns (OriginationLibrary.RolloverAmounts memory amounts) {
+
) internal view returns (OriginationLibrary.RolloverAmounts memory, uint256 repayAmount) {
    // get total interest to close v3 loan
    uint256 interest = IRepaymentControllerV3(repaymentControllerV3).getInterestAmount(
        oldLoanData.terms.principal,
        oldLoanData.terms.proratedInterestRate
    );
+
    // calculate the repay amount to settle V3 loan
+
    repayAmount = oldLoanData.terms.principal + interest;
+
    return(
        rolloverAmounts(
            oldLoanData.terms.principal,
@@ -277,7 +282,7 @@ contract OriginationControllerMigrate is IMigrationBase,
OriginationController,
            borrowerFee,
            lenderFee,
        )
+
        ), repayAmount
    );
}
@@ -298,7 +303,8 @@ contract OriginationControllerMigrate is IMigrationBase,
OriginationController,
LoanLibrary.LoanTerms memory newLoanTerms,
address borrower_,
address lender,
OriginationLibrary.RolloverAmounts memory _amounts
+
OriginationLibrary.RolloverAmounts memory _amounts,
+
uint256 repayAmount
) internal {
    // cache borrower address for flash loan callback
    borrower = borrower_;
@@ -308,7 +314,7 @@ contract OriginationControllerMigrate is IMigrationBase,
OriginationController,
    // flash loan amount = new principal + any difference supplied by borrower
    uint256[] memory amounts = new uint256[](1);
    amounts[0] = _amounts.amountFromLender + _amounts.needFromBorrower - _amounts.amountToBorrower;
+
    amounts[0] = repayAmount;
    bytes memory params = abi.encode(
        OriginationLibrary.OperationData(
```
