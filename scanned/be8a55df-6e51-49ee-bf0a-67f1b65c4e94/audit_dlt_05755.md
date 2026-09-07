# [?] [Storage] Fix HotState crash on stale merged_state

## Summary
Severity: Unknown
Chain: Aptos
Component: aptos-labs/aptos-core
Published: 2026-02-20
Source: https://github.com/aptos-labs/aptos-core/commit/eb4770408398ee63af674ff51e935a30a3880c7a
Type: security-commit

## Details
[Storage] Fix HotState crash on stale merged_state

The `Committer` thread could panic at `layer.rs:123` (`base_layer.inner.layer >= self.inner.base_layer`)
when building a delta between `merged_state` and an incoming `to_commit` state.

**Root cause**: `State::update()` spawns new `MapLayer` shards with
`base_layer = persisted_snapshot.shard.layer()`. When old
`LayeredHotStateView` readers prevent `try_merge()` from advancing
`merged_state`, the committer's `merged_state` falls behind
`persisted_snapshot`. Subsequent `to_commit.make_delta(&merged_state)` then
violates the layer compatibility invariant.

**Fix**: Before building the delta, spin-wait for old views to drain so
`try_merge()` can advance `merged_state` to a compatible layer. One successful
merge is always sufficient since `persisted.layer <= previous_committed.layer`.

- Add `MapLayer::can_view_after()` — non-panicking compatibility check
- Add `State::can_be_delta_base_of()` — checks all 16 shards
- `Committer::try_merge()` now returns `bool` (`false` = blocked by old views)
- `Committer::run()` waits for merge before `make_delta` when incompatible

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>
