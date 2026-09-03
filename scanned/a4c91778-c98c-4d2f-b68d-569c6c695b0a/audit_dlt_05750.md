# [?] [consensus] Fix rand manager deadlock in multi-block batches (#19359)

## Summary
Severity: Unknown
Chain: Aptos
Component: aptos-labs/aptos-core
Published: 2026-04-07
Source: https://github.com/aptos-labs/aptos-core/commit/fefcfade3edf26f0396d63963f7ea04364f3666f
Type: security-commit

## Details
[consensus] Fix rand manager deadlock in multi-block batches (#19359)

PR #18699 introduced a circular dependency for multi-block ordering
batches: later blocks' has_rand_txns_fut waits for earlier blocks'
execute_fut, which waits for rand_rx, which is only sent after the
entire batch is dequeued from the rand manager — but dequeue requires
all blocks' randomness to be decided first.

Fix: eagerly send rand_tx in PipelinedBlock::set_randomness (matching
the pattern of set_decryption_key), so the pipeline is unblocked as
soon as randomness is decided per-block. The execution_schedule_phase
already handles this idempotently via .take().

Co-authored-by: Claude Opus 4.6 (1M context) <noreply@anthropic.com>
