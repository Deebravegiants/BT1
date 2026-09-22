# [M] 6.1 Possible Revert Due to Underflow

## Summary
Severity: Medium
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
Design Medium Version 1 Code Corrected

Should the recorded DAI balance of the DSProxy at the Vat exceed the amount required to repay the
debt, the subtraction in DssProxyActionsCharter._getWipeAllWad() will underflow causing the
transaction to revert.

Code corrected:

_getWipeAllWad() now returns 0 when enough DAI is available to cover the debt.
