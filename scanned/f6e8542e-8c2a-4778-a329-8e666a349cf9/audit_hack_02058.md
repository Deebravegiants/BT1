# [M] 6.13 Possible to Frontrun on Claim Request

## Summary
Severity: Medium
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
Design Medium Version 1 Specification Changed

In some situations, e.g., the price of the underlying token changes significantly, one (or more) liquidity
providers might want to exit their positions and call function claim() to remove their liquidity from
float. However, an attacker might frontrun this transaction and call function borrow() and prevent
the liquidity provider from exiting their position.

```
Version 3 Specification changed
```
The respective code has been removed according to the new specifications of Version 3.
