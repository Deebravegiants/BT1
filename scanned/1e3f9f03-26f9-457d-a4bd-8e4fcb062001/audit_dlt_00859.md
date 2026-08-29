# [?] fix(en): Fix race condition in EN storage initialization (#3515)

## Summary
Severity: Unknown
Chain: zkSync
Component: matter-labs/zksync-era
Published: 2025-01-23
Source: https://github.com/matter-labs/zksync-era/commit/c916797d49d636c9e642264786d4124ebd338ec3
Type: security-commit

## Details
fix(en): Fix race condition in EN storage initialization (#3515)

## What ❔

Reworks `NodeStorageInitializer::is_chain_tip_correct()` so that it
performs the minimum amount of work possible, i.e. detects whether the
latest L1 batch / L2 block diverge or not.

## Why ❔

EN storage initialization is prone to a data race: the "is storage
initialized" check calls
`NodeStorageInitializer::is_chain_tip_correct()`, which internally
performs the entire iteration of the reorg detector (in particular,
binary search for the first diverged block). This can lead to a data
race with block revert logic, which may be executed concurrently. This
data race was observed on the revert integration tests.

## Checklist

- [x] PR title corresponds to the body of PR (we generate changelog
entries from PRs).
- [x] Tests for the changes have been added / updated.
- [x] Documentation comments have been added / updated.
- [x] Code has been formatted via `zkstack dev fmt` and `zkstack dev
lint`.
