# [?] Fixing race condition for archival queries missing uncommited_changes (#2671)

## Summary
Severity: Unknown
Chain: Sovereign SDK
Component: Sovereign-Labs/sovereign-sdk
Published: 2026-04-01
Source: https://github.com/Sovereign-Labs/sovereign-sdk/commit/f3efa4d76e57b572964bcc0fb4311a588f74fc05
Type: security-commit

## Details
Fixing race condition for archival queries missing uncommited_changes (#2671)

* Initial fix for the flaky EVM test

* Stabilizing EVM block pinned tests part 1

* Stabilizing EVM block pinned tests part 2

* Repalce the branch-local ignore_changes_after_height with unconditional

* Add tests

* Bring back accidentally removed queries.rs

* Changelog and commit cleanup

* Tests simplification

* Remove useless test. Proper test will follow

* Add an actual test

* Remove comment and expand test
