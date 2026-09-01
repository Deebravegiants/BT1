# [?] fix(tests): make all temp_dir usages in tests nondeterministic to avoid collisions (#11189)

## Summary
Severity: Unknown
Chain: IOTA
Component: iotaledger/iota
Published: 2026-04-14
Source: https://github.com/iotaledger/iota/commit/d49476f37c7740c3cadc158d576a3d6a7609d807
Type: security-commit

## Details
fix(tests): make all temp_dir usages in tests nondeterministic to avoid collisions (#11189)

# Description of change

Replace `std::env::temp_dir()` and raw `tempfile::tempdir()` with
`iota_common::tempdir()` in tests.

## Summary

- Replace all uses of `std::env::temp_dir()` in test code with
`iota_common::tempdir()`
- Replace all direct `tempfile::tempdir()` calls in test code with
`iota_common::tempdir()`
- Add `iota-common` dev-dependency to `iota-data-ingestion-core` and
`iota-archival`

## Motivation

After upgrading RocksDB, unrelated PRs (still on the old version)
started failing with "unsupported version 6" SST file errors. This
revealed that CI test runners were sharing database paths because tests
used `std::env::temp_dir()` directly, which always resolves to the same
`/tmp` directory. This also explains long-standing flaky tests where
RocksDB complained about databases already being opened.

Additionally, several test files had local `temp_dir()` helpers that
called `tempfile::tempdir()` directly, bypassing the
`nondeterministic!()` macro. In `simtests`, deterministic RNG seeding
can cause `tempfile::tempdir()` to produce identical paths across test
runs, leading to the same class of collisions.

`iota_common::tempdir()` is the existing utility that solves both
problems: it creates a unique random directory via `tempfile::tempdir()`
and wraps it in `nondeterministic!()` to ensure uniqueness even under
`simtest` determinism.

## How the change has been tested


_Trimmed to 38 lines — full report: https://github.com/iotaledger/iota/commit/d49476f37c7740c3cadc158d576a3d6a7609d807_
