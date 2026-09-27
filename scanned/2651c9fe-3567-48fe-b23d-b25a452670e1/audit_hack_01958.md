# [M] 5.2 Interfaces Not Implemented / Available

## Summary
Severity: Medium
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
Correctness Medium Version 1 Risk Accepted

Morpho does not extend the IMorpho interface. This can lead to errors during development and
integration by third parties as the interface might not match up with the implementations. Indeed, the
IMorpho interface lacks some public functions like setInterestRates or incentivesVault.

Risk accepted:

Morpho Labs accepts the risk and tries to maintain correct interfaces.
