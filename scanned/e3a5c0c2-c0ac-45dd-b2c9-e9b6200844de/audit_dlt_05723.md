# [?] fix(state): handle invalidateblock/reconsiderblock edge cases without panicking (#10592)

## Summary
Severity: Unknown
Chain: Zcash
Component: ZcashFoundation/zebra
Published: 2026-06-25
Source: https://github.com/ZcashFoundation/zebra/commit/d58097f8793aa6122e9b5c5becd11c26d397401b
Type: security-commit

## Details
fix(state): handle invalidateblock/reconsiderblock edge cases without panicking (#10592)

* fix(state): handle invalidateblock/reconsiderblock edge cases without panicking

Three authenticated state-control RPC sequences could panic the
non-finalized write task, which is process-fatal under `panic = "abort"`:

1. `invalidateblock` on the root of a tracked non-finalized chain called
   `BTreeSet::remove(&chain)`, which compared the stored chain against
   itself and reached `Chain::cmp`'s `unreachable!()` for matching tip
   hashes.
2. `invalidateblock` on two same-height sibling fork tips with the same
   parent: the second invalidation produced a shortened parent chain
   whose tip hash matched an existing entry, and `BTreeSet::insert`
   reached the same `unreachable!()` while comparing.
3. `reconsiderblock` repeated for the same successfully reconsidered
   hash: the first call removed the invalidation record from a clone of
   `invalidated_blocks` instead of from the live map, so the second
   call replayed the same chain suffix into a chain set that already
   contained the restored tip and hit the same `Chain::cmp` panic. The
   replay path also used `Chain::push(...).expect(...)` for unexpected
   failures.

Changes:

- `Chain::cmp` returns `Ordering::Equal` for chains with matching
  cumulative work and tip hash. The `BTreeSet<Arc<Chain>>` already
  treats equal items as duplicates, so this keeps the uniqueness
  invariant via no-op inserts instead of a panic.
- `NonFinalizedState::invalidate_block` root branch retains the chain
  set by tip hash instead of `BTreeSet::remove(&chain)`. The non-root
  branch is unchanged at the call site, but is now idempotent against
  same-tip-hash collisions because `Chain::cmp` no longer panics.
- `NonFinalizedState::reconsider_block` copies the height out of the
  invalidation lookup, then calls `shift_remove(&height)` on the live
  map (not a clone). The replay loop returns the typed
  `ReconsiderError::ReplayFailed(ValidateContextError)` instead of
  `expect()`.

_Trimmed to 38 lines — full report: https://github.com/ZcashFoundation/zebra/commit/d58097f8793aa6122e9b5c5becd11c26d397401b_
