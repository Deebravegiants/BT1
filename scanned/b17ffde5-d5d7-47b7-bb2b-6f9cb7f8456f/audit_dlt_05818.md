# [?] fix(indexer): surface shard-tracking errors instead of panicking on restart (#15872)

## Summary
Severity: Unknown
Chain: NEAR
Component: near/nearcore
Published: 2026-06-29
Source: https://github.com/near/nearcore/commit/fec195197c76dca36853cfb62664d28b13b4cf4b
Type: security-commit

## Details
fix(indexer): surface shard-tracking errors instead of panicking on restart (#15872)

`build_streamer_message` used to panic with "`receipt` must be present
at this moment" on restart (issue
https://github.com/near/nearcore/issues/15867, Mode A).
The chain was: on restart `ShardTracker::cares_about_shard` runs an
epoch lookup that can fail transiently and masks the error as `false`,
so `fetch_block_new_chunks` spuriously drops a chunk for a shard the
node actually tracks.
That shard's execution outcomes are then never classified by the
per-chunk loop and fall into the leftover loop, which unwrapped a `None`
receipt on the shard's transaction outcomes and panicked.

Fixes the root cause for the indexer:

- shard_tracker: add `ShardTracker::cares_about_shard_result`, which
returns the `EpochError` instead of masking it. `cares_about_shard` and
friends keep their bool signatures via a thin `unwrap_or(false)`, so
consensus call sites are unchanged; only the indexer opts into the
fallible variant.
- `fetch_block_new_chunks` now propagates that error, so
`build_streamer_message` returns `Err` and the streamer retries the
block instead of producing a message with orphaned outcomes.

Caveat:
Re-indexing historical blocks produced before a node adopted
https://github.com/near/nearcore/pull/14981 would have `receipt: None`
with no store entry, and now errors (streamer retries) instead of
reconstructing.

Partially fixed #15867 (Mode A).
