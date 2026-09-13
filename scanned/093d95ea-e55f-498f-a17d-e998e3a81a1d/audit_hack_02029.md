# [M] 6.10 maxAmount Can Be Circumvented

## Summary
Severity: Medium
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
Design Medium Version 1 Code Corrected

When opening a credit account, a check of the amount invested is performed:

```
require(
amount >= minAmount && amount <= maxAmount,
Errors.CM_INCORRECT_AMOUNT
);
```
By limiting the amount originally invested, one can limit the amount of leverage that can be borrowed by
the pool. However, this limitation can be circumvented as follows:

```
1.The user opens an account with an allowed account.
2.She calls CreditManager.addCollateral.
3.She calls increaseBorrowedAmount.
```
Note, that addCollateral does not perform any checks and increaseBorrowedAmount only checks
that the borrowed amount does not turn the account unhealthy.

Code Corrected:

The implementation has been extended to prevent increasing the borrowed amount more than the
predetermined maximum:


```
require(
borrowedAmount.add(amount) <
maxAmount.mul(maxLeverageFactor).div(
Constants.LEVERAGE_DECIMALS
),
Errors.CM_INCORRECT_AMOUNT
);
```
