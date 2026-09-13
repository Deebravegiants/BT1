# [M] 6.30 Missing Sanity Checks in signOrder

## Summary
Severity: Medium
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
Security Medium Version 1 Code Corrected

The function signOrder in LStrategy performs some sanity checks if the submitted order is in line
with the values of the posted preOrder. However, the check for order.receiver is missing, therefore
the caller can set any arbitrary address and receive the buyToken.

Code corrected:

The code doing the sanity checks for order in signOrder has been moved to the separate function
LStrategyOrderHelper.checkOrder which includes the check that the receiver is the
erc20Vault.
