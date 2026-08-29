# [?] [indexer] Fix potential overflow in ending version calculation (#18828)

## Summary
Severity: Unknown
Chain: Aptos
Component: aptos-labs/aptos-core
Published: 2026-02-23
Source: https://github.com/aptos-labs/aptos-core/commit/1fa8dca6e867a8c01850a5595081f51676a6ac65
Type: security-commit

## Details
[indexer] Fix potential overflow in ending version calculation (#18828)

Use saturating_add instead of unchecked addition when computing
ending_version from starting_version + transactions_count, preventing
overflow when both values are large u64s.

Co-authored-by: Claude Opus 4.6 (1M context) <noreply@anthropic.com>
