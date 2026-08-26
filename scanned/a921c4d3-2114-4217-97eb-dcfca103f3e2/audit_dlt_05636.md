# [?] stagedsync, db: fix TxLookup prune crash with membatch cursor during FCU (#20122)

## Summary
Severity: Unknown
Chain: Ethereum
Component: erigontech/erigon
Published: 2026-03-24
Source: https://github.com/erigontech/erigon/commit/cabda2a61f6783250d1cd192fa5e299097fabdf5
Type: security-commit

## Details
stagedsync, db: fix TxLookup prune crash with membatch cursor during FCU (#20122)

## Summary

- During FCU, the pipeline runs on a `membatchwithdb.MemoryMutation`
(block overlay). The TxLookup prune stage's type switch only handled
`*mdbx.MdbxCursor`, causing a crash when it received
`*memoryMutationCursor`:
  ```
unexpected cursor type *membatchwithdb.memoryMutationCursor for table
BlockTransactionLookup
  ```
- Adds a generic `kv.RwCursorPseudoDupSort` wrapper that makes any
`RwCursor` satisfy `PseudoDupSortRwCursor` for non-DupSort tables (same
semantics as the existing MDBX-specific wrapper)
- Applied the same defensive fix to domain and history prune type
switches

Observed on blob-devnet-0 at block 327898 ([slot
424431](https://dora.blob-devnet-0.ethpandaops.io/slot/424431)).

## Test plan

- [ ] Verify on blob-devnet-0 that FCU no longer crashes at the TxLookup
prune stage
- [ ] `make lint` passes
- [ ] `make test-short` passes

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-authored-by: Claude Opus 4.6 (1M context) <noreply@anthropic.com>
