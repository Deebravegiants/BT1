# [?] [consensus] Clear module cache on pipeline teardown to prevent hot-state deadlock

## Summary
Severity: Unknown
Chain: Aptos
Component: aptos-labs/aptos-core
Published: 2026-03-16
Source: https://github.com/aptos-labs/aptos-core/commit/f064f03a4312cfae80d6e3647cd40714acb003d7
Type: security-commit

## Details
[consensus] Clear module cache on pipeline teardown to prevent hot-state deadlock

The `PipelineBuilder` holds a `module_cache` containing a
`CachedModuleView<CachedStateView>`, where the inner `CachedStateView`
keeps an `Arc<dyn HotStateView>` alive. When the consensus observer
aborts its pipeline (e.g. on epoch transition or fallback to state
sync), spawned tasks are correctly cancelled but the `PipelineBuilder`
itself — and its `module_cache` — remains alive until a new pipeline is
created (at the start of the next epoch).

This creates a circular deadlock:

- The stale `HotStateView` in `module_cache` keeps the `Weak` ref in
  `old_views` alive (`strong_count > 0`), blocking `try_merge`.
- `try_merge` being blocked stalls the hot-state commit thread, filling
  up the commit channel (backlog = 10).
- The full channel blocks `state_batch_committer`, which blocks
  `StateSnapshotCommitter`, which blocks `BufferedState::enqueue_commit`.
- State-sync threads can no longer commit checkpoints, so state sync
  stalls.
- The new `PipelineBuilder` (which would replace the old one and drop
  the stale cache) is only created **after** state sync completes and a
  new epoch starts — deadlock.

Fix: call `clear_module_cache()` in `clear_pending_block_state()`, the
common teardown path used by fallback entry, subscription failure, and
post-sync reset. This drops the stale `CachedStateView` and its
`HotStateView` reference immediately, allowing `try_merge` to proceed.

As an extra safety net, the hot-state committer now force-clears
`old_views` after 5 seconds of blocked merge, logging an error so
the root cause is still surfaced.

Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>
