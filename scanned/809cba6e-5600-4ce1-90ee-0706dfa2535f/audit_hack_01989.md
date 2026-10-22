# [M] 6.3 Incorrect Accounting of Global Debt

## Summary
Severity: Medium
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
Correctness Medium Version 1 Code Corrected

The following issue was reported by Angle during the review process. The function _closeVault in the
contract VaultManager.sol does not update the global debt state variable totalNormalizedDebt.

Code corrected:

The function _closeVault has been revised to update the global debt state when a vault is closed:
totalNormalizedDebt -= vault.normalizedDebt;.
