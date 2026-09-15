# [M] 5.3 Loan Default Frontrunning

## Summary
Severity: Medium
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
Security Medium Version 1 Risk Accepted

In Live state, and if withdrawals are enabled, lenders in any tranche can withdraw the full amount even if
there are open loans that are using some of the available funds. Consider the following example:

- Each tranche has a value of 100 tokens.
- A loan for 150 tokens has been issued.
- Users of the junior tranche now withdraw all 100 tokens.
- The loan defaults resulting in the value of the senior tranche being reduced to 50.

If the users in the junior tranche observe the call to StructuredPortfolio.markLoanAsDefaulted,
they can frontrun it to redeem all of their tokens, while the other tranches suffer from the loss.

Risk accepted:

TrueFi accepted the risk giving the following statement:

```
Shouldn’t occur, but in case managers want to be safe, withdrawals can be disabled before calling
StructuredPortfolio.markLoanAsDefaulted.
```
