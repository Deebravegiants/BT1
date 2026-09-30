# [M] New lenders are unfairly charged for interestFee when rolling over an loan

## Summary
Severity: Medium
Contest weight: 0.7512
Dataset id: 3031
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In rolloverAmounts(), interestFee is added to amountFromLender:
```solidity
if (borrowerFee > 0 || lenderFee > 0 || interestFee > 0) {
    unchecked {
        borrowerOwedForNewLoan = newPrincipalAmount - borrowerFee;
        amounts.amountFromLender = newPrincipalAmount + lenderFee + interestFee;
    }
} else {
```
However, this means that the new lender incurs the interest fee from the old loan, which is not ideal as the lender of the new loan should not be charged for anything related to the old loan. As a result, the new lender will be forced to pay more when entering a loan using rolloverLoan() as compared to initializeLoan(). For comparison, in RepaymentController._prepareRepay(), which is used in repay() and forceRepay(), the interest fee is charged to the loan's lender:
```solidity
// the amount to send to the lender
amountToLender = amountFromBorrower - interestFee - principalFee;
```

## Recommendation
In rolloverAmounts(), add interestFee to amountFromLender only when the old and new lender are the same:
```solidity
if (borrowerFee > 0 || lenderFee > 0 || interestFee > 0) {
    unchecked {
        borrowerOwedForNewLoan = newPrincipalAmount - borrowerFee;
        amounts.amountFromLender = newPrincipalAmount + lenderFee + interestFee;
+
        amounts.amountFromLender = newPrincipalAmount + lenderFee;
+
+
        if (lender == oldLender) {
+
            amounts.amountFromLender += interestFee;
+
        }
    }
} else {
```
In the scenario where the new and old lender are different, subtract interestFee from the amount repaid to the old lender:
```solidity
OriginationCalculator.sol#L78-L81
// Calculate lender amounts based on if the lender is the same as the old lender
if (lender != oldLender) {
    // different lenders, repay old lender
    amounts.amountToOldLender = repayAmount;
+
    amounts.amountToOldLender = repayAmount - interestFee;
```
