# [M] 6.4 Stuck Ether

## Summary
Severity: Medium
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
Security Medium Version 1 Code Corrected

The function angle in the contract VaultManager is declared as payable, however the code has no
logic to deal with the incoming Ether. Therefore, the Ether sent when calling the function angle is not
accounted and gets stuck into the contract.

Code corrected:

The keyword payable has been removed from the function VaultManager.angle, hence users
cannot send Ether to the contract when calling this function.
