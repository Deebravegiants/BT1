# [M] 5.2 DoS for Start

## Summary
Severity: Medium
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
Design Medium Version 1 Risk Accepted

The manager can turn the system Live by calling StructuredPortfolio.start(). When this is
done, the system checks if the ratios of the values stored in each tranche are appropriate. If it is not, the
transaction reverts. This means that depositing or withdrawing an amount - if allowed - before the
manager calls start can block the system from turning live since the ratios will not be correct. The
depositController and withdrawController enforce a ceiling and a floor respectively but the
issue can still arise.

Risk accepted:

TrueFi accepted the risk giving the following statement:

```
Shouldn’t occur, but in case managers want to be safe, withdrawals and deposits can be disabled
before starting the portfolio.
```
