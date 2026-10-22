# [H] 5.1 Defaulted Loan Repayment

## Summary
Severity: High
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
Design High Version 1 Acknowledged

Loans can be marked to be repayable after default. In the case of a defaulted loan being repaid later,
new investors of the equity tranche gain an unfair advantage over users that invested in the tranche
before the loan has been marked as defaulted.

This behavior can even be exploited by borrowers to regain some of the repaid loan by investing in the
equity tranche after the default of their own loan. Consider the following example (assuming no fees and
interest for simplification):

- A portfolio consists of 3 tranches and is in Live status with no active loans.
- Users have deposited 100 tokens to each tranche with no accrued interest (i.e., 1 share per token).
- A new loan of 99 tokens is issued to a borrower.
- After some time, the manager marks the loan as defaulted.
- The value of the equity tranche is now 1 token with a total supply of 100 shares.
- The borrower deposits 100 tokens into the equity tranche and receives 10,000 shares back.
- The borrower repays the loan, raising the equity tranche's value to 200 tokens.
- The borrower is now entitled to ~198 tokens in the tranche.

Issue acknowledged:

TrueFi replied:


```
we are aware of this issue, but it's more of manager responsibility to pause deposits/withdrawals in
case of risk in portfolio (so before marking loan as defaulted manager should first disable
deposits/withdrawals)
```
