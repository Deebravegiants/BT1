# [M] lenderFee and interestFee may not be collected from new lenders

## Summary
Severity: Medium
Contest weight: 0.6055
Dataset id: 3023
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In OriginationCalculator.rolloverAmounts(), under the following two conditions:
1. lender == oldLender
2. borrowerOwedForNewLoan < repayAmount < amountFromLender
The lenderFee and interestFee will not be collected from the new lender and will not be paid. Additionally, a portion of borrowFee isn't paid as newPrincipalAmount - repayAmount isn't collected from the new lender. When both conditions listed above are true:
• amounts.leftoverPrincipal will be 0, so no amount is collected from the new lender
• amountToLender will be 0, so no fees are subtracted from the amount sent to the new lender
As such, the ”costs” to the new lender aren't accounted for or collected. As a result, the protocol and old/new loan affiliates will lose out on fees.
For example, assuming payableCurrency is USDC:
repayAmount = 80
newPrincipalAmount = 100
borrowerFee = lenderFee = interestFee = 30
borrowerOwedForNewLoan = newPrincipalAmount - borrowerFee = 100 - 30 = 70
amounts.amountFromLender = newPrincipalAmount + lenderFee + interestFee = 100 + 30 + 30 = 160
amounts.needFromBorrower = repayAmount - borrowerOwedForNewLoan = 80 - 70 = 10
Only 10 USDC was collected from the borrower, and there were no other transfers. Therefore, only 10 USDC will be accrued as the borrowerFee.
The missing funds are:
• lenderFee and interestFee, which are 30 USDC each.
• A portion of borrowerFee, more specifically, 20 USDC.
The sum of these missing funds is equal to amounts.amountFromLender - repayAmount, which was supposed to be collected from the new lender.
Additional Note: The current V3 OriginationController live contract also contains the same bug, but all fees are currently set to 0.

## Recommendation
When borrowerOwedForNewLoan < repayAmount < amountFromLender, set amounts.leftoverPrincipal as amounts.amountFromLender - repayAmount:
```solidity
if (repayAmount > borrowerOwedForNewLoan) {
+
    if (repayAmount < amounts.amountFromLender) {
+
        amounts.leftoverPrincipal = amounts.amountFromLender - repayAmount;
+
    }
    // amount to collect from borrower
    unchecked {
        amounts.needFromBorrower = repayAmount - borrowerOwedForNewLoan;
    }
} else {
```
This will collect the missing funds from the lender when lender == oldLender. Additionally, modify _rollover() to collect leftoverPrincipal when needFromBorrower > 0, similar to the logic in OriginationControllerMigrate._migrate():
```solidity
// Collect funds based on settle amounts and total them
uint256 settledAmount;
if (lender != oldLender) {
    // If new lender, take new principal from new lender
    payableCurrency.safeTransferFrom(lender, address(this),
    amounts.amountFromLender);
    settledAmount += amounts.amountFromLender;
- }
+ } else if (amounts.leftoverPrincipal > 0) {
+
    payableCurrency.safeTransferFrom(lender, address(this),
    amounts.leftoverPrincipal);
+
    settledAmount += amounts.leftoverPrincipal;
+ }
if (amounts.needFromBorrower > 0) {
    // Borrower owes from old loan
    payableCurrency.safeTransferFrom(borrower, address(this),
    amounts.needFromBorrower);
    settledAmount += amounts.needFromBorrower;
- } else if (amounts.leftoverPrincipal > 0 && lender == oldLender) {
    // If same lender, and new amount from lender is greater than old loan repayment amount,
    // take the difference from the lender
    payableCurrency.safeTransferFrom(lender, address(this),
    amounts.leftoverPrincipal);
    settledAmount += amounts.leftoverPrincipal;
```
