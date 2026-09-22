# [C] nimiq-blockchain is missing a wall-clock upper bound on block timestamps

## Summary
Severity: Critical
Chain: nimiq-blockchain
Component: nimiq-blockchain
CVE: CVE-2026-40093
CWE: Improper Input Validation, Improper Validation of Specified Quantity in Input
Published: 2026-04-10
Source: https://github.com/advisories/GHSA-49xc-52mp-cc9j
Type: github-advisory

## Details
### Impact

Block timestamp validation enforces that `timestamp >= parent.timestamp` for non-skip blocks and `timestamp == parent.timestamp + MIN_PRODUCER_TIMEOUT` for skip blocks, but there is no visible upper bound check against the wall clock. A malicious block-producing validator can set block timestamps arbitrarily far in the future. This directly affects reward calculations via `Policy::supply_at()` and `batch_delay()` in `blockchain/src/reward.rs`, inflating the monetary supply beyond the intended emission schedule.

### Patches
TBD

### Workarounds
No know workarounds.
