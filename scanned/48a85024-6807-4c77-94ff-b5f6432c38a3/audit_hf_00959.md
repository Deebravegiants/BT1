# [H] OriginationCalculator._calculateRolloverAmounts() doesnt account for partially repaid loans

## Summary
Severity: High
Contest weight: 0.6113
Dataset id: 3016
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
OriginationCalculator._calculateRolloverAmounts() calls rolloverAmounts() with oldLoanData.terms.principal, which is the loan's entire principal:

```solidity
return rolloverAmounts(
    oldLoanData.terms.principal,
    interest,
```

However, it should call rolloverAmounts() with oldLoanData.balance instead as partial repayments are now possible in V4. The borrower could have repaid part of the old loan's principal before it is rolled over into a new loan.

For rollovers, this will cause the borrower to overpay when rolloverLoan() is called since repayAmount, the amount of principal + interest the borrower needs to repay for the old loan, will be higher than it should be.

This is highly likely to occur when borrowerOwedForNewLoan > repayAmount in rolloverAmounts() as rolloverLoan() will not transfer any funds from the borrower.

For refinancing loans, RefinanceController.refinanceLoan() will incorrectly pull the whole oldLoanData.terms.principal from the new lender and overpay to the old lender.

For example:
- Borrower is lent 1e18, i.e. terms.principal is 1e18 (assuming 0 fees or interest)
- Borrower repays 5e17, i.e borrower has 5e17 and lender has 5e17
- A new lender decided to refinance with smaller interest but the same principal of 1e18, i.e. has to repay 5e17 to the old lender and transfer 5e17 to the borrower
- _calculateRolloverAmounts() calculates amountToOldLender = 1e18 - the old lender is overpaid (now has 1e18 + 5e17) and borrower doesn't receive anything, leaving him with 5e17

## Recommendation
Replace oldLoanData.terms.principal with oldLoanData.balance, which is the amount of principal yet to be repaid:

```diff
return rolloverAmounts(
    oldLoanData.terms.principal,
+
    oldLoanData.balance,
```
