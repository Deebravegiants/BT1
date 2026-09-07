# [?] fix(op-acceptance): eliminate race condition in super fault proof L1 head capture (#19805)

## Summary
Severity: Unknown
Chain: Optimism
Component: ethereum-optimism/optimism
Published: 2026-03-31
Source: https://github.com/ethereum-optimism/optimism/commit/c865cf8108725b158b5447aac780d3fdd0bcc0a3
Type: security-commit

## Details
fix(op-acceptance): eliminate race condition in super fault proof L1 head capture (#19805)

* fix(op-acceptance): fix flaky VariedBlockTimes by restructuring batcher choreography

The test captured L1 heads by querying the supernode's RequiredL1 values
via l1BlockWithLocalSafeBlocks, which races with continued sequencer block
production shifting those values. Instead, read the L1 head directly from
the L1 client at each stage of the batcher choreography — the invariants
(which chain's data is on L1) are maintained by which batchers are running,
not by timing windows.

Also removes the t.Skip() from all four VariedBlockTimes test variants.

Fixes ethereum-optimism/optimism#19804

Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>

* fix(op-acceptance): apply race-free batcher choreography to all super fault proof tests

Apply the same pattern used for RunVariedBlockTimesTest to
RunSuperFaultProofTest and RunSingleChainSuperFaultProofSmokeTest.
Replace l1BlockWithLocalSafeBlocks polling with direct L1 head reads
from the L1 client, using batcher start/stop state as the
synchronization mechanism.

Remove the now-unused l1BlockWithLocalSafeBlocks helper and the "math"
import it required.

Fixes ethereum-optimism/optimism#19804

Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>

* fix(op-acceptance): stop batchers after capturing L1 heads to prevent cleanup failure

The t.Cleanup(Batcher.Start) calls registered in Stage 1 fail with
"batcher is already running" if the batchers are still running at test
teardown. Stop them after capturing l1HeadCurrent so the cleanup can
restart them cleanly.

_Trimmed to 38 lines — full report: https://github.com/ethereum-optimism/optimism/commit/c865cf8108725b158b5447aac780d3fdd0bcc0a3_
