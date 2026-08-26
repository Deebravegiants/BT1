# [?] Wait for blocksync goroutines on Stop to fix leveldb shutdown panic (#3415)

## Summary
Severity: Unknown
Chain: Sei
Component: sei-protocol/sei-chain
Published: 2026-05-15
Source: https://github.com/sei-protocol/sei-chain/commit/a27b9d64d394745a28e08f22c92cc666d6dfcb8c
Type: security-commit

## Details
Wait for blocksync goroutines on Stop to fix leveldb shutdown panic (#3415)

Reactor.OnStart and BlockPool.OnStart started their long-running
goroutines (requestRoutine, poolRoutine, processBlockSyncCh,
processPeerUpdates, makeRequestersRoutine) with raw `go fn(ctx)` using
the outer context. They were therefore not registered with the
BaseService WaitGroup, and Stop() never waited for them. The outer ctx
also outlived Stop, so the goroutines kept running after Stop returned.

During node shutdown this raced nodeImpl.OnStop's blockStore.Close():
poolRoutine, still inside SaveBlock -> Base() -> bs.db.Iterator,
observed its leveldb table reader released and panicked with
"leveldb/table: reader released".

Route each goroutine through BaseService.Spawn so it is tracked by the
WaitGroup and bound to inner.ctx. Stop() now cancels them and blocks
until they exit, which happens before the node closes the BlockStore DB.
Add a regression test that asserts no blocksync goroutines remain after
Reactor.Stop() returns.

<!-- CURSOR_SUMMARY -->
---

> [!NOTE]
> **Medium Risk**
> Changes blocksync/consensus goroutine lifecycles and shutdown
ordering; mistakes could cause hangs or missed transitions, but the
change is localized and covered by a new regression test.
> 
> **Overview**
> Fixes blocksync shutdown races by moving long-running goroutines off
raw `go` launches and onto `BaseService.Spawn`/`SpawnCritical`, ensuring
`Stop()` cancels the correct context and waits for all blocksync
routines to exit before the block store is closed.
> 
> Adds readiness gates (`blocksyncReady`, `consensusReady`) so routines
can be pre-spawned in `Reactor.OnStart` yet only begin work when block
sync starts or the consensus handoff completes, and updates

_Trimmed to 38 lines — full report: https://github.com/sei-protocol/sei-chain/commit/a27b9d64d394745a28e08f22c92cc666d6dfcb8c_
