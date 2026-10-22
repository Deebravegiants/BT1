# [H] Incorrect fee calculation when migrating V3 loans in OriginationControllerMigrate.migrateV3Loan()

## Summary
Severity: High
Contest weight: 0.7950
Dataset id: 3014
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
OriginationControllerMigrate.migrateV3Loan() calls _initializeMigrationLoan() with amounts.amountFromLender and amounts.amountToBorrower:

```solidity
// initialize v4 loan
_initializeMigrationLoan(newTerms, msg.sender, lender, amounts.amountFromLender, amounts.amountToBorrower);
```

However, amounts.amountFromLender and amounts.amountToBorrower here are different from the expected values of _amountFromLender and _amountToBorrower in LoanCore.startLoan().

_initializeMigrationLoan() directly passes amounts.amountFromLender and amounts.amountToBorrower into startLoan(), which calculates the fees earned by the protocol using the difference of both values:

```solidity
// Assign fees for withdrawal
uint256 feesEarned;
unchecked { feesEarned = _amountFromLender - _amountToBorrower; }
```

amountFromLender - amountToBorrower here is actually not equal to the fees earned from migrating a V3 loan.

According to rolloverAmounts():
```solidity
amountFromLender = newPrincipalAmount + lenderFee + interestFee
```

When repayAmount > borrowerOwedForNewLoan:
```solidity
amountToBorrower = 0
```
amountFromLender - amountToBorrower = newPrincipalAmount + lenderFee + interestFee

Otherwise, with some simple algebra:
```solidity
amountToBorrower = borrowerOwedForNewLoan - repayAmount
```
amountFromLender - amountToBorrower = repayAmount + lenderFee + interestFee + borrowerFee

As seen from above, amountFromLender - amountToBorrower will always include newPrincipalAmount or repayAmount. Additionally, borrowerFee will be excluded when repayAmount > borrowerOwedForNewLoan.

This will cause feesEarned to end up becoming a largely inflated value. Since fees are distributed between the protocol and affiliates, affiliates will be able to withdraw more fees than intended, causing a loss of fees for the protocol.

## Recommendation
When calling startLoan() in _initializeMigrationLoan(), pass amountFromLender as borrowerFee + lenderFee and amountToBorrower as 0:

```diff
// create loan in LoanCore
- newLoanId = loanCore.startLoan(lender, borrower_, newTerms, amountFromLender, amountToBorrower, feeSnapshot);
+ newLoanId = loanCore.startLoan(lender, borrower_, newTerms, borrowerFee + lenderFee, 0, feeSnapshot);
```

Consider removing the amountFromLender and amountToBorrower parameters from _initializeMigrationLoan() as they are no longer needed:

```diff
function _initializeMigrationLoan(
    LoanLibrary.LoanTerms memory newTerms,
    address borrower_,
    address lender,
+   address lender,
    uint256 amountFromLender,
    uint256 amountToBorrower
) internal returns (uint256 newLoanId) {
```

In migrateV3Loan():
```diff
// initialize v4 loan
- _initializeMigrationLoan(newTerms, msg.sender, lender, amounts.amountFromLender, amounts.amountToBorrower);
+ _initializeMigrationLoan(newTerms, msg.sender, lender);
```

Arcade: Fixed in PR-96. A refactoring is introduced where LoanCore.startLoan() now takes a feesEarned param, calculated in the OC contracts.
