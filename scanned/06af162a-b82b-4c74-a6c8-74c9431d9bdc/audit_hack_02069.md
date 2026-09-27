# [M] 7.9 Reentrancy When Creating Perpetual Position

## Summary
Severity: Medium
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
Security Medium Version 2 Code Corrected

When creating a new perpetual position there is a possibility for a reentrancy attack. During the mint()
operation of the token a callback is triggered that can be used for a reentrancy attack.

Among other things, possible consequences of such an attack could be:

- that the coverage exceeds the expected values
- that a non-liquidatable perpetual exists
- that a mismatch between NFTs and positions exists

Code corrected:

The call to _mint() is done after all state changes.
