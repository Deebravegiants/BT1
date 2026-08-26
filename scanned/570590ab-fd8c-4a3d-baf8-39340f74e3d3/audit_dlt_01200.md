# [?] caplin: fix chain_reorg Server-Sent Event depth underflow and wrong old_head_block (#21440)

## Summary
Severity: Unknown
Chain: Ethereum
Component: erigontech/erigon
Published: 2026-06-04
Source: https://github.com/erigontech/erigon/commit/cfe582c7ff73be7d45bb4fd5965cab6ebf113f6e
Type: security-commit

## Details
caplin: fix chain_reorg Server-Sent Event depth underflow and wrong old_head_block (#21440)

## Summary
- **depth** was computed as `newHeadSlot - forkPoint`, which could
underflow to `2^64 - 2`; now correctly computed as `oldHeadSlot -
forkPoint`
- **old_head_block** contained the common ancestor root instead of the
previous canonical tip; now uses `ReadCanonicalHead` (`cursor.Last()`)
to capture the actual old tip before mutations
- **1-slot reorgs** were silently missed because the old `parentRoot !=
oldCanonical` check compared identical values; replaced with
`currentSlot < oldHeadSlot`

Fixes #20885

## Test plan
- [x] `TestUpdateCanonicalChainReorgEvent` — same-length 2-slot reorg
- [x] `TestUpdateCanonicalChainReorgShorterFork` — old chain longer than
new fork
- [x] `TestUpdateCanonicalChainReorgLongerFork` — new fork longer than
old chain
- [x] `TestUpdateCanonicalChainNoReorg` — normal chain extension (no
event emitted)
- [x] `TestUpdateCanonicalChainReorgOneSlot` — minimal 1-slot reorg
(depth=1)
- [x] `make erigon` builds
- [x] `golangci-lint` clean on changed packages

🤖 Generated with [Claude Code](https://claude.com/claude-code)

---------

Co-authored-by: Claude Opus 4.6 <noreply@anthropic.com>
