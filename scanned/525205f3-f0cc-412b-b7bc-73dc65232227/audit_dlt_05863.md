# [?] fix(kona-node): handle missing L1 origin block in sequencer instead of panicking (#19945)

## Summary
Severity: Unknown
Chain: Optimism
Component: ethereum-optimism/optimism
Published: 2026-04-08
Source: https://github.com/ethereum-optimism/optimism/commit/8e333b19ec185321c7c7ae85e4b5f7a087b9a220
Type: security-commit

## Details
fix(kona-node): handle missing L1 origin block in sequencer instead of panicking (#19945)

The origin selector could panic with `unreachable!()` when
`get_block_by_hash` returned `Ok(None)` — e.g. during an L1 reorg or
sync lag. Replace the panic with an `OriginNotFound` error and trigger
an engine reset in the sequencer actor so the node recovers gracefully.

A real-world example of this bug is in [this] ci run.

[this]: https://app.circleci.com/pipelines/github/ethereum-optimism/optimism/121941/workflows/391e49ef-49fb-4a52-a18b-c73e3bb0ee9d/jobs/4753970/tests

Co-authored-by: Claude Opus 4.6 (1M context) <noreply@anthropic.com>
