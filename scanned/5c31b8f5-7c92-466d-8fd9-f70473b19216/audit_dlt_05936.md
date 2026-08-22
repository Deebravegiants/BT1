# [?] SMTChecker: Fix crash in BMC engine regarding state variables

## Summary
Severity: Unknown
Chain: Solidity
Component: ethereum/solidity
Published: 2025-01-10
Source: https://github.com/argotorg/solidity/commit/57342666ca9b03499d8299b3ff269494647b6787
Type: security-commit

## Details
SMTChecker: Fix crash in BMC engine regarding state variables

Previously, analyzing a call to a getter to a contract then has not been
analyzed yet with BMC would result in a crash because BMC would not know
about the state variable being accessed.

To fix this, we let BMC know about all state variables in all contracts
during initialization.
