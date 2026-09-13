# [M] 6.3 Allowances Not Completely Disabled

## Summary
Severity: Medium
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
Correctness Medium Version 1 Code Corrected

BasicDelegationPod overwrites and inhibits functions transfer, transferFrom and approve. The
increaseAllowance and decreaseAllowance functions inherited from OpenZeppelin's ERC
implementation are not overridden and hence can be used.

Code corrected:

The functions increaseAllowance and decreaseAllowance have been explicitely disabled.
