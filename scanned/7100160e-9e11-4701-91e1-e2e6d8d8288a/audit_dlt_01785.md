# [?] fix(gateway_balances): handle overflow exception: (#4355)

## Summary
Severity: Unknown
Chain: XRP
Component: XRPLF/rippled
Published: 2023-03-16
Source: https://github.com/XRPLF/rippled/commit/10555faa928bc02400c22f1856ad1846b5d52f1a
Type: security-commit

## Details
fix(gateway_balances): handle overflow exception: (#4355)

* Prevent internal error by catching overflow exception in `gateway_balances`.
* Treat `gateway_balances` obligations overflow as max (largest valid) `STAmount`.
  * Note that very large sums of STAmount are approximations regardless.

---------

Co-authored-by: Scott Schurr <scott@ripple.com>
