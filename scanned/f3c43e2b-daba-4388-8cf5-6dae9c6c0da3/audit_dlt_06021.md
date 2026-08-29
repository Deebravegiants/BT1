# [?] fix: group reconciliation votes by block_id to resolve same-block deadlock (#3269)

## Summary
Severity: Unknown
Chain: Fuel
Component: FuelLabs/fuel-core
Published: 2026-04-17
Source: https://github.com/FuelLabs/fuel-core/commit/f7826d1c1b58cdfeabbf44bc7b671a7b14ea3039
Type: security-commit

## Details
fix: group reconciliation votes by block_id to resolve same-block deadlock (#3269)

## Summary

- Fixes a PoA reconciliation deadlock observed on devnet 2026-04-17
where the same block ended up on all 6 Redis nodes with three different
epochs, causing permanent livelock
- `unreconciled_blocks` now groups votes by `block_id` only, tracking
max epoch as a tiebreaker. Identical blocks written during re-promotion
storms count toward quorum.
- Added a regression test that reproduces the exact production error
string

## The bug

During re-promotion storms (two pods racing for leadership), the same
block can be written to different Redis nodes with different epochs. The
old vote grouping `(epoch, block_id)` fragmented these identical blocks
into separate vote groups:

```
Node state (same block_id, different epoch stamps):
  1a-0, 1a-1, 1b-1: epoch 268 → vote group A, count=3
  1b-0:            epoch 269 → vote group B, count=1
  1c-0, 1c-1:      epoch 270 → vote group C, count=2  ← max-epoch winner

Required quorum: 4.  Winner count: 2 → repair attempted.
Repair writes the winner to all 6 nodes → HEIGHT_EXISTS on every node
(each has SOME entry at that height) → Written=0 → total=2 < quorum.
Permanent livelock.
```

## The fix

Group by `block_id` alone; track max epoch per block_id as the
tiebreaker when block_ids genuinely differ:

```rust
```

_Trimmed to 38 lines — full report: https://github.com/FuelLabs/fuel-core/commit/f7826d1c1b58cdfeabbf44bc7b671a7b14ea3039_
