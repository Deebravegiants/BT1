# [?] Fix an overflow during balance calculation when waiting for compound transaction acceptance. (#393)

## Summary
Severity: Unknown
Chain: Kaspa
Component: kaspanet/rusty-kaspa
Published: 2024-01-15
Source: https://github.com/kaspanet/rusty-kaspa/commit/fb5e304f558810bcd70fb16e3afb97759a39c28c
Type: security-commit

## Details
Fix an overflow during balance calculation when waiting for compound transaction acceptance. (#393)

* Fix balance calculation overflow when waiting for compound transaction acceptance.

* account for fees in compound transactions
