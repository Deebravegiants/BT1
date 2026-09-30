# [M] 6.5 Maker Deposit Action Uses Full Balance

## Summary
Severity: Medium
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
Correctness Medium Version 1 Code Corrected

While the DepositData struct contains an amount parameter, the maker/Deposit action always
uses the full available balance. This behavior is not documented and may be unexpected for users who
specify an inferior amount.

Code partially corrected:

The code of action maker/Deposit now deposits the amount specified. However the action still exchanges
all Ether balance to WETH. Is this intended?

Code corrected:

The code wrapping ETH has been removed. This fixes the remaining issue as the user's Ether will not be
exchanged to WETH. Note that the user needs to have WETH available instead.
