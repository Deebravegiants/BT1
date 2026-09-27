# [?] execution/execmodule: fix data race between background prune and next FCU (#21697)

## Summary
Severity: Unknown
Chain: Ethereum
Component: erigontech/erigon
Published: 2026-06-12
Source: https://github.com/erigontech/erigon/commit/16b8af16d4fe8f98c35e689c2c2c2540333549f9
Type: security-commit

## Details
execution/execmodule: fix data race between background prune and next FCU (#21697)

## Symptom

The hive `engine-cancun` test **"Re-Org Back into Canonical Chain,
Depth=5"** intermittently fails against erigon with `INVALID` /
`"Invalid chain after execution"`: the forward re-org executes zero
blocks, the head stays behind, and the handler reports `bad forkchoice`.

## Root cause

With `FcuBackgroundPrune=true` (the node default), `updateForkChoice`
launched the prune in a goroutine but released the FCU semaphore without
waiting for it, so the prune's `Sync.RunPrune` raced the next FCU's
`Sync.RunLoop` on the same pipeline `Sync` — the next FCU could skip its
execution stage and leave the head un-advanced. The background-commit
path had a sibling hole: its goroutine released the semaphore with no
ordering against the FCU goroutine's cleanup defers
(`ResetPendingUpdates` on `e.currentContext`,
`forkValidator.ClearWithUnwind`), racing the next request's
`e.currentContext` writes once it acquired the semaphore.

## Fix

The semaphore is the sole gate for the pipeline `Sync` and the module's
FCU state, so it is now released only after both the FCU's cleanup and
the background work are done:

- The background prune/commit goroutine holds the semaphore until it
finishes and releases it on exit. The FCU response is still sent without
waiting; a concurrent op returns `ExecutionStatusBusy` → `SYNCING`
(retried by the CL), as background-commit already behaved.
- All FCU cleanup runs before the semaphore is handed to the goroutine:
overlay teardown (`PublishOverlay(nil)` + `SharedDomains.Close()`, which
also frees the SD RAM immediately instead of holding it through the
prune), then `ResetPendingUpdates` + `ClearWithUnwind` as a once-guarded
function invoked eagerly at the handoff. Any follow-up op that acquires
the semaphore observes fully-settled state.

## Testing

- `TestReorgBackAndForwardIntoCanonicalChain` (new) replays the hive
sequence with `fg-prune`, `bg-prune`, and `bg-commit`; passes under
`-race`. The final head assertion is guarded by `ExecModule.WaitIdle` so
it isn't timing-dependent.
- Both races were proven red→green under the race detector by
temporarily widening the racy windows with sleep probes — the test DB
uses `DisableFsync`, so its ~50µs prune doesn't force the overlap
deterministically.
- Existing reorg/FCU tests and the full `execution/execmodule` package
pass under `-race`; `make lint` clean; `make erigon integration` builds.

---------

Co-authored-by: noop <noop@noop>

### execution/execmodule/exec_module.go
```diff
@@ -192,7 +192,11 @@ type ExecModule struct {
 	blockReader services.FullBlockReader
 
 	// MDBX database
-	db               kv.TemporalRwDB // main database
+	db kv.TemporalRwDB // main database
+	// semaphore is the module's single mutual-exclusion domain: it guards the
+	// pipeline Sync and all FCU state. Ops either TryAcquire and report Busy
+	// (retried by the CL) or block, and the background FCU commit/prune
+	// goroutines inherit the semaphore, releasing it only when their work is done.
 	semaphore        *semaphore.Weighted
 	forkValidator    *ForkValidator
 	pipelineExecutor *PipelineExecutor
```

### execution/execmodule/exec_module_test.go
```diff
@@ -349,6 +349,83 @@ func TestUpdateForkChoiceForwardExecutesAfterStateAheadRecovery(t *testing.T) {
 	}))
 }
 
+// Exercises the hive engine-cancun "Re-Org Back into Canonical Chain" scenario:
+// after producing each block N>5 the CL re-orgs the head back to block 5 and
+// then forward to N, re-applying blocks 6..N. With background prune enabled
+// (the node default) the prune runs on the shared pipeline sync, and before the
+// fix it could race the next FCU's RunLoop, skip the execution stage and leave
+// the head behind ("Invalid chain after execution"). Run under -race.
+func TestReorgBackAndForwardIntoCanonicalChain(t *testing.T) {
+	modes := []struct {
+		name string
+		opt  execmoduletester.Option
+	}{
+		{name: "fg-prune"},
+		// bg-prune matches the hive erigon default (FcuBackgroundPrune=true): the
+		// background prune shares the pipeline sync with the next FCU's RunLoop.
+		// bg-commit hands the semaphore to its goroutine the same way; in both
+		// modes the handoff must not overlap the FCU goroutine's cleanup.
+		{name: "bg-prune", opt: execmoduletester.WithFcuBackgroundPrune()},
+		{name: "bg-commit", opt: execmoduletester.WithFcuBackgroundCommit()},
+	}
+	for _, mode := range modes {
+		opts := []execmoduletester.Option{execmoduletester.WithGenesisSpec(&types.Genesis{Config: chain.AllProtocolChanges})}
+		if mode.opt != nil {
+			opts = append(opts, mode.opt)
+		}
+		t.Run(mode.name, func(t *testing.T) {
+			ctx := t.Context()
+			m := execmoduletester.New(t, opts...)
+
+			const chainLen = 9
+			const reorgBackTo = 5
+			chainPack, err := blockgen.GenerateChain(m.ChainConfig, m.Genesis, m.Engine, m.DB, chainLen, func(i int, b *blockgen.BlockGen) {})
+			require.NoError(t, err)
+			require.Len(t, chainPack.Blocks, chainLen)
+
+			headerAt := func(n uint64) *types.Header { return chainPack.Blocks[n-1].Header() }
+
+			for n := uint64(1); n <= chainLen; n++ {
+				// Insert the block only when it is "produced" (as newPayload would):
+				// later blocks must not exist in the DB during the earlier re-orgs.
+				insRes, err := insertBlocks(ctx, m.ExecModule, chainPack.Blocks[n-1:n])
+				require.NoError(t, err)
+				require.Equalf(t, execmodule.ExecutionStatusSuccess, insRes, "insert block %d", n)
+
+				h := headerAt(n)
+				vr, err := validateChain(ctx, m.ExecModule, h)
+				require.NoError(t, err)
+				require.Equalf(t, execmodule.ExecutionStatusSuccess, vr.ValidationStatus, "validate block %d", n)
+				ur, err := updateForkChoice(ctx, m.ExecModule, h)
+				require.NoError(t, err)
+				require.Equalf(t, execmodule.ExecutionStatusSuccess, ur.Status, "fcu to canonical block %d", n)
+
+				if n <= reorgBackTo {
+					continue
+				}
+				// Re-org the head back down to block 5.
+				back, err := updateForkChoice(ctx, m.ExecModule, headerAt(reorgBackTo))
+				require.NoError(t, err)
+				require.Equalf(t, execmodule.ExecutionStatusSuccess, back.Status, "re-org back to block %d (cycle at %d)", reorgBackTo, n)
+
+				// Re-org the head forward back into the canonical chain (block n).
+				fwd, err := updateForkChoice(ctx, m.ExecModule, h)
+				require.NoError(t, err)
+				require.Equalf(t, execmodule.ExecutionStatusSuccess, fwd.Status, "re-org forward back to canonical block %d", n)
+				require.Equalf(t, h.Hash(), fwd.LatestValidHash, "forward re-org should make block %d the head", n)
+			}
+
+			// Let the last FCU's commit and prune (foreground or background)
+			// settle before reading the committed head.
+			m.ExecModule.WaitIdle(ctx)
+			require.NoError(t, m.DB.ViewTemporal(ctx, func(tx kv.TemporalTx) error {
+				require.Equal(t, headerAt(chainLen).Hash(), rawdb.ReadHeadBlockHash(tx), "head must be at canonical tip")
+				return nil
+			}))
+		})
+	}
+}
+
 func addTwoTxnsToPool(ctx context.Context, startingNonce uint64, t *testing.T, m *execmoduletester.ExecModuleTester, txpool txpoolproto.TxpoolServer, baseFee uint64) {
 	tx2, err := types.SignTx(types.NewTransaction(startingNonce, common.Address{1}, uint256.NewInt(10_000), params.TxGas, uint256.NewInt(baseFee), nil), *types.LatestSignerForChainID(m.ChainConfig.ChainID), m.Key)
 	require.NoError(t, err)
```

### execution/execmodule/forkchoice.go
```diff
@@ -23,6 +23,7 @@ import (
 	"math"
 	"runtime"
 	"strconv"
+	"sync"
 	"time"
 
 	"github.com/erigontech/erigon/common"
@@ -119,9 +120,10 @@ func (e *ExecModule) UpdateForkChoice(ctx context.Context, headHash, safeHash, f
 	// it is not cancelled when the caller's context times out. We return as soon
 	// as the result lands on outcomeCh — for a merge-extending fork at tip the
 	// result is sent before flush/commit, so the consensus client is not blocked
-	// on the EL commit. The forkchoice goroutine releases the semaphore only after
-	// all cleanup defers have run, so any follow-up op (AssembleBlock, next FCU)
-	// that acquires the semaphore observes fully-settled state.
+	// on the EL commit. The semaphore is released — by the forkchoice goroutine, or
+	// by the background commit/prune goroutine it hands off to — only after the FCU
+	// cleanup has run, so any follow-up op (AssembleBlock, next FCU) that acquires
+	// the semaphore observes fully-settled state.
 	go func() {
 		if err := e.updateForkChoice(e.bacgroundCtx, headHash, safeHash, finalizedHash, outcomeCh); err != nil {
 			e.logger.Debug("updateforkchoice failed", "err", err)
@@ -169,12 +171,15 @@ func (e *ExecModule) updateForkChoice(ctx context.Context, originalBlockHash, sa
 	}()
 
 	defer UpdateForkChoiceDuration(time.Now())
-	defer e.forkValidator.ClearWithUnwind()
-	defer func() {
+	// The next semaphore acquirer must observe settled state, so the bg-commit/
+	// bg-prune paths run this eagerly before handing the semaphore to their goroutine.
+	cleanupBeforeSemaRelease := sync.OnceFunc(func() {
 		if e.currentContext != nil {
 			e.currentContext.ResetPendingUpdates()
 		}
-	}()
+		e.forkValidator.ClearWithUnwind()
+	})
+	defer cleanupBeforeSemaRelease()
 
 	var validationError string
 	type canonicalEntry struct {
@@ -675,6 +680,7 @@ func (e *ExecModule) updateForkChoice(ctx context.Context, originalBlockHash, sa
 			bgSD := currentContext
 			currentContext = nil
 			dispatcher := e.pipelineExecutor.Dispatcher()
+			cleanupBeforeSemaRelease()
 			go func() {
 				defer e.semaphore.Release(1)
 				defer bgSD.Close()
@@ -707,7 +713,22 @@ func (e *ExecModule) updateForkChoice(ctx context.Context, originalBlockHash, sa
 		// Only runs in foreground when both background flags are off.
 		if !e.fcuBackgroundCommit {
 			if e.fcuBackgroundPrune {
+				// RunPrune shares the pipeline Sync with the next FCU's RunLoop,
+				// so the goroutine holds the semaphore until done. Tear the overlay
+				// down here (prune doesn't use it) to free the SD immediately, and
+				// so the outer defer can't clear it after the next FCU publishes
+				// its own.
+				shouldReleaseSema = false
+				if dispatcher := e.pipelineExecutor.Dispatcher(); dispatcher != nil {
+					dispatcher.PublishOverlay(nil)
+				}
+				if currentContext != nil {
+					currentContext.Close()
+					currentContext = nil
+				}
+				cleanupBeforeSemaRelease()
 				go func() {
+					defer e.semaphore.Release(1)
 					pruneTimings, err := e.runForkchoicePrune(initialCycle)
 					if err != nil && !errors.Is(err, context.Canceled) {
 						e.logger.Error("Error running background prune", "err", err)
```
