# [?] node, commitment: fix parallel exec deadlock on many-core machines (#22408)

## Summary
Severity: Unknown
Chain: Ethereum
Component: erigontech/erigon
Published: 2026-07-22
Source: https://github.com/erigontech/erigon/commit/4d6ef27f954fb17372f18c3a355e64ca2a3d4aad
Type: security-commit

## Details
node, commitment: fix parallel exec deadlock on many-core machines (#22408)

## Problem

On machines with ≥32 hardware threads (`runtime.NumCPU()`), the
engineapi tests deadlock deterministically when parallel execution is
enabled:

- `TestEngineApiUnwindRedoStateChurnPreservesState`
-
`TestEngineApiExecBlockBatchWithLenLtMaxReorgDepthAtTipThenUnwindShouldSucceed`

`engine_forkchoiceUpdated` stalls for the full 30s timeout, then fails
with `apply loop exited ... block(s) had tx-results without a
blockResult`.

Root cause: embedded/test nodes fall back to a hardcoded **32-slot**
read-tx semaphore in `node.OpenDatabase` (the CLI binary uses the
`--db.read.concurrency` default, `min(max(10, GOMAXPROCS*64), 9000)`, so
it is unaffected). Parallel exec spawns `NumCPU` workers, each lazily
opening a **long-lived read tx it keeps even while idle**. With `NumCPU
>= 32` the workers alone exhaust the semaphore: during unwind/redo,
`resetWorkers` rolls back the workers' txs, and on resume the freed
slots are re-acquired FIFO by whoever is queued — including commitment
warmup workers. A worker that has already claimed a task from the shared
queue can end up parked in `semaphore.Acquire` forever: its task is not
stealable, the other workers sit idle holding their slots, and the whole
pipeline (exec loop → apply loop → FCU) wedges. Commitment warmup
workers blocked in the same `Acquire` also held `Warmuper.CloseAndWait`
hostage, as their acquisition context is not cancellable from the
warmuper.

The defect has always been present: the 32-slot fallback dates back to
the original `node.OpenDatabase` code, and any embedded node with enough
exec workers could in principle exhaust it. It became much more likely
to trigger with #21240, which raised the parallel exec worker count from
`NumCPU/2` to `NumCPU`, lowering the deadlock threshold from ≥64 to ≥32
hardware threads — i.e. into the range of common development machines.
CI never caught it because GitHub runners have 4–16 cores, keeping
workers well below the 32 slots.

The same starvation is reachable on two more configurations, both
flagged in review, because the semaphore default is a function of
`GOMAXPROCS` while the worker count is a function of `NumCPU` — the two
can diverge:
- an explicitly low `--db.read.concurrency` (the flag help suggested low
values for validators) — reproduced with `DBReadConcurrency=8` /
`EXEC3_WORKERS=8`;
- a reduced `GOMAXPROCS` on a many-core host (Go 1.25 may lower it under
a CPU quota) — the `GOMAXPROCS*64` default can fall below the
`NumCPU`-derived worker count.

## Fix

1. **Read-tx semaphore floored at the exec worker count** — the limit is
now `max(configured-or-default, execWorkers+1+reserved)`, computed in a
shared `httpcfg.RoTxsLimit` used by both the `--db.read.concurrency`
flag default and `node.OpenDatabase`. Because the floor derives from the
worker count (the same `NumCPU`-based quantity that sizes the pool)
rather than `GOMAXPROCS`, the two sizes can no longer diverge: the
semaphore always exceeds the permanent readers (the `execWorkers+1` pool
txs plus the apply-loop tx), with reserved headroom for transient
commitment/RPC readers. This closes all three exposed configs with one
mechanism:
- the hardcoded 32-slot embedded fallback — embedded/test nodes now size
the semaphore from the same formula as the CLI, and never below the
worker count;
- an **explicitly low** `--db.read.concurrency` (e.g. `8`) — raised to
the floor, with a one-time `log.Warn` at flag resolution
(`SetEthConfig`) so the override is visible; the flag help no longer
documents a low value as safe;
- a **reduced `GOMAXPROCS`** — the `GOMAXPROCS*64` default could fall
below the worker count; the floor prevents it.

The prior read-tx-limit default (`httpcfg.DefaultDBReadConcurrency`, the
`min(max(10, GOMAXPROCS*64), 9000)` formula) is still the baseline
`RoTxsLimit` starts from; it is now defined once and reused by
`flags.go` and `cmd/mcp`.

2. **Commitment warmup never queues on the read-tx semaphore** —
`warmupTrieContextFactory` tags its context with
`kv.WithNonBlockingAcquire` (the fail-fast mechanism introduced in
#19905/#20303 for RPC overload). Warmup is a best-effort page-cache
prefetch: if no slot is free it is skipped (`TryAcquire` →
`ErrReadTxLimitExceeded`), instead of parking warmup workers in the FIFO
queue where they steal slots from exec workers.

3. **`Warmuper.CloseAndWait` can no longer be held hostage** — the
trie-context factory is now ctx-aware and runs synchronously in the
worker; a factory blocked opening its read tx (e.g. parked on the
semaphore) is unblocked on shutdown by cancelling its ctx: the factories
open their read tx directly under the warmuper's lifecycle ctx, which is
a child of the exec ctx (`ComputeCommitment` passes the same ctx to the
factories and to `Process` → `NewWarmuper`), so outer cancellation still
propagates. Because the factory runs synchronously, no factory code can
outlive `CloseAndWait`.

The first iteration of this point ran the factory in a detached
goroutine and abandoned it on shutdown. That let factory code outlive
`CloseAndWait` and race with the exec loop's `SetStateReader` — every
race-detector CI job on this PR failed with that data race (142/142
reports pointed at the detached goroutine). Reworked in the second
commit to the synchronous ctx-aware design. A third commit (review)
removed the interim `beginRoCancellableBy` two-ctx merge as redundant
given the parent/child relationship above — the merged ctx was also
stored in the returned `MdbxTx` and cancelled on factory return, which
would have broken any later range iterator on a worker tx. Per review,
`TrieContextFactory` is a single ctx-aware type (no separate
`WarmupTrieContextFactory`), threaded through `ParallelPatriciaHashed`,
`StreamingCommitter` and `streaming_deep_fold.go`.

4. **Warmup worker fails fast on a nil trie context** — if the
trie-context factory returns a nil `PatriciaContext` while the warmuper
ctx is still live, the worker now returns an explicit error (cancelling
the errgroup) instead of exiting successfully. A silent exit previously
left `w.work` with no consumer, hanging `WarmKey` once the buffer
filled. The cancelled-ctx case (legitimate shutdown) still returns
`ctx.Err()`, so `CloseAndWait` behavior is unchanged.

## Verification

TDD: each fix was driven by a test written first and observed failing
for the right reason. The two review-follow-up fixes were confirmed red
against the pre-fix behavior and green with the fix:
`httpcfg.RoTxsLimit` floor cases (e.g. `RoTxsLimit(8,8)` expected 31,
got 8 without the floor) and
`TestWarmuperNilFactoryResultUnblocksProducers` (5s `WarmKey` hang
without the explicit error).

| Scenario (32-thread machine, `ERIGON_EXEC3_PARALLEL=true`) | Before |
After |
|---|---|---|
| The two engineapi tests above | deterministic FAIL, ~31.5s (30s FCU
stall) | PASS in ~12.8s, stable at `-count=3` |
| Same, with `GOMAXPROCS=4` | FAIL (semaphore stayed at 32) | PASS ~1.6s
|
| Same, with `ERIGON_EXEC3_WORKERS=16` | PASS (workers < slots) | PASS
~1.5s |
| `DBReadConcurrency=8` + `EXEC3_WORKERS=8` (review repro) |
deterministic FCU stall, 30s | PASS (floor raises 8→31) |
| `go test -race` on `execution/commitment/...` + full `TestEngineApi*`
suite | 142 DATA RACE reports in CI race jobs | 0 races, green |
| `execution/commitment/...`, `node`, `httpcfg` full suites | — | green
|
| `make lint` / `make erigon integration` | — | clean / build OK |

**Re-verified after the review rework (da32ed8a61) on a 32-thread
machine** (`runtime.NumCPU() = 32`, the configuration that reproduced
the original deadlock), with `ERIGON_EXEC3_PARALLEL=true`:
- the two formerly-deadlocking engineapi tests pass at `-count=3` (~5.8s
per run, no FCU stall)
- full `execution/engineapi` suite green (~83s)
- `go test -race -count=1 ./execution/commitment/...` green (0 races)
- `make lint` clean (two consecutive runs)

**Review follow-up (P1/P2 read-tx floor):** the `RoTxsLimit` floor, the
explicit-value `log.Warn`, the flag-help update, and the warmup
nil-context error are added in commit d8e1151a13. A second review round
(7d43da1b57) makes the floor derive from the per-node configuration:
`eth.New` stamps the resolved `Sync.ExecWorkerCount` into
`nodecfg.ExecWorkerCount` before opening the ChainDB, so embedded
callers that never touch `dbg.Exec3Workers` are covered by construction
(end-to-end engineapi test asserts the wiring, red without the stamp);
the floor counts the full census of long-lived holders —
`execPermanentReadTxs = 5` (extra pool worker, exec-loop, apply-loop,
block-loader, commitment-calculator txs) plus `execReadAheadTxs = 2` for
the block read-ahead txs of the steady tip-following mode; and the
GOMAXPROCS>NumCPU test assumption is replaced with the floor invariant
`RoTxsLimit(0, NumCPU) > NumCPU + execPermanentReadTxs +
execReadAheadTxs`. `httpcfg`, `node`, `nodecfg`, `cmd/utils`,
`execution/commitment` suites and `make lint` are green on the touched
packages.

---------

Co-authored-by: Alex Sharov <AskAlexSharov@gmail.com>

### cmd/mcp/main.go
```diff
@@ -23,7 +23,6 @@ import (
 	"os"
 	"os/signal"
 	"path/filepath"
-	"runtime"
 	"syscall"
 	"time"
 
@@ -232,7 +231,7 @@ func runDatadirMode(ctx context.Context, logger log.Logger, dataDir, privAPI, lo
 		WithDatadir:       true,
 		PrivateApiAddr:    privAPI,
 		TxPoolApiAddr:     privAPI, // inherit from private API, same as rpcdaemon
-		DBReadConcurrency: min(max(10, runtime.GOMAXPROCS(-1)*64), 9_000),
+		DBReadConcurrency: httpcfg.DefaultDBReadConcurrency(),
 	}
 
 	db, backend, txPool, mining, stateCache, blockReader, engine, ff, bridgeReader, heimdallReader, err :=
```

### cmd/rpcdaemon/cli/httpcfg/http_cfg.go
```diff
@@ -18,6 +18,7 @@ package httpcfg
 
 import (
 	"net"
+	"runtime"
 	"time"
 
 	"github.com/erigontech/erigon/db/datadir"
@@ -27,6 +28,38 @@ import (
 	"github.com/erigontech/erigon/rpc/rpchelper"
 )
 
+// DefaultDBReadConcurrency is the default MDBX read-tx semaphore size;
+// rationale in DBReadConcurrencyFlag's usage.
+func DefaultDBReadConcurrency() int {
+	return min(max(10, runtime.GOMAXPROCS(-1)*64), 9_000)
+}
+
+// execPermanentReadTxs counts the long-lived read txs a parallel batch always
+// holds beyond the worker count: the extra pool worker, the exec-loop and
+// apply-loop txs, the block-loader tx and the commitment-calculator tx.
+const execPermanentReadTxs = 5
+
+// execReadAheadTxs counts the block read-ahead txs held on non-initial applying
+// cycles — the steady tip-following mode — so they are counted with the fixed
+// holders rather than eating into the reserve.
+const execReadAheadTxs = 2
+
+// dbReadTxsReserved is read-tx headroom kept above parallel exec's permanent
+// holders. Without it a transient commitment/RPC reader can take the last slot
+// a blocked permanent holder needs, deadlocking the pipeline.
+const dbReadTxsReserved = 16
+
+// RoTxsLimit sizes the MDBX read-tx semaphore, flooring it at the parallel-exec
+// worker count plus reserved headroom; the configured value (or derived default
+// when unset) wins only when already above the floor.
+func RoTxsLimit(dbReadConcurrency, execWorkers int) int64 {
+	limit := DefaultDBReadConcurrency()
+	if dbReadConcurrency > 0 {
+		limit = dbReadConcurrency
+	}
+	return int64(max(limit, execWorkers+execPermanentReadTxs+execReadAheadTxs+dbReadTxsReserved))
+}
+
 type HttpCfg struct {
 	Enabled bool
 
```

### cmd/rpcdaemon/cli/httpcfg/http_cfg_test.go
```diff
@@ -0,0 +1,57 @@
+// Copyright 2026 The Erigon Authors
+// This file is part of Erigon.
+//
+// Erigon is free software: you can redistribute it and/or modify
+// it under the terms of the GNU Lesser General Public License as published by
+// the Free Software Foundation, either version 3 of the License, or
+// (at your option) any later version.
+//
+// Erigon is distributed in the hope that it will be useful,
+// but WITHOUT ANY WARRANTY; without even the implied warranty of
+// MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
+// GNU Lesser General Public License for more details.
+//
+// You should have received a copy of the GNU Lesser General Public License
+// along with Erigon. If not, see <http://www.gnu.org/licenses/>.
+
+package httpcfg
+
+import (
+	"runtime"
+	"testing"
+
+	"github.com/stretchr/testify/require"
+)
+
+func TestReadTxLimitCoversExecReaders(t *testing.T) {
+	t.Parallel()
+	// The limit must exceed every long-lived read tx a parallel batch holds
+	// (see execPermanentReadTxs and execReadAheadTxs) even when GOMAXPROCS is
+	// set below NumCPU and shrinks the derived default.
+	require.Greater(t, RoTxsLimit(0, runtime.NumCPU()), int64(runtime.NumCPU()+execPermanentReadTxs+execReadAheadTxs))
+}
+
+func TestRoTxsLimit(t *testing.T) {
+	t.Parallel()
+	defaultLimit := int64(DefaultDBReadConcurrency())
+	floor := func(workers int) int64 {
+		return int64(workers + execPermanentReadTxs + execReadAheadTxs + dbReadTxsReserved)
+	}
+	for _, tc := range []struct {
+		name         string
+		cfg, workers int
+		want         int64
+	}{
+		{"default passes through when above floor", 0, 4, defaultLimit},
+		{"high explicit value passes through", 5000, 8, 5000},
+		{"low explicit value raised to floor", 8, 64, floor(64)},
+		// pins the census: 8 workers + 5 fixed holders + 2 read-ahead + 16 reserve
+		{"explicit value equal to worker count raised", 8, 8, 31},
+		{"default floored below worker count", 0, int(defaultLimit) + 1, floor(int(defaultLimit) + 1)},
+	} {
+		t.Run(tc.name, func(t *testing.T) {
+			t.Parallel()
+			require.Equal(t, tc.want, RoTxsLimit(tc.cfg, tc.workers))
+		})
+	}
+}
```

### cmd/utils/flags.go
```diff
@@ -44,6 +44,7 @@ import (
 	"github.com/erigontech/erigon/cl/clparams"
 	"github.com/erigontech/erigon/cl/clparams/devgenesis"
 	"github.com/erigontech/erigon/cmd/downloader/downloadernat"
+	"github.com/erigontech/erigon/cmd/rpcdaemon/cli/httpcfg"
 	"github.com/erigontech/erigon/cmd/utils/flags"
 	"github.com/erigontech/erigon/common"
 	libkzg "github.com/erigontech/erigon/common/crypto/kzg"
@@ -403,8 +404,8 @@ var (
 	}
 	DBReadConcurrencyFlag = cli.IntFlag{
 		Name:  "db.read.concurrency",
-		Usage: "Ceiling on concurrent open DB read transactions (MDBX read-tx semaphore); extra readers wait for a slot rather than error. Default scales as min(max(10, GOMAXPROCS*64), 9000) — kept well above CPU count because reads are I/O-bound, and capped below Go's ~10K OS-thread limit. Low values are fine for low read-concurrency nodes (e.g. validators); raise it for nodes serving heavy parallel RPC",
-		Value: min(max(10, runtime.GOMAXPROCS(-1)*64), 9_000),
+		Usage: "Ceiling on concurrent open DB read transactions (MDBX read-tx semaphore); extra readers wait for a slot rather than error. Default scales as min(max(10, GOMAXPROCS*64), 9000) — kept well above CPU count because reads are I/O-bound, and capped below Go's ~10K OS-thread limit. A value below the parallel-exec worker count is raised to it (each worker holds a long-lived read tx, so a lower ceiling would deadlock); to actually reduce read concurrency, lower --exec.workers instead",
+		Value: httpcfg.DefaultDBReadConcurrency(),
 	}
 	RpcMaxConcurrentRequestsFlag = cli.IntFlag{
 		Name:  "rpc.max.concurrency",
@@ -2031,6 +2032,12 @@ func SetEthConfig(nodeCtx context.Context, ctx *cli.Command, nodeConfig *nodecfg
 		dbg.SetExec3Workers(1)
 		cfg.ExecWorkerCount = 1
 	}
+	if c := ctx.Int(DBReadConcurrencyFlag.Name); c > 0 {
+		if limit := httpcfg.RoTxsLimit(c, cfg.ExecWorkerCount); int64(c) < limit {
+			logger.Warn("db.read.concurrency below the exec read-tx floor; raising to avoid a parallel-exec deadlock",
+				"configured", c, "using", limit, "execWorkers", cfg.ExecWorkerCount)
+		}
+	}
 	if ctx.IsSet(ExecNoMergeFlag.Name) {
 		dbg.SetNoMerge(ctx.Bool(ExecNoMergeFlag.Name))
 	}
```

### execution/commitment/commitment_test.go
```diff
@@ -44,7 +44,7 @@ func (n *noopPatriciaContext) Account(plainKey []byte) (*Update, error) { return
 func (n *noopPatriciaContext) Storage(plainKey []byte) (*Update, error) { return nil, nil }
 func (n *noopPatriciaContext) TxNum() uint64                            { return 0 }
 
-func noopCtxFactory() (PatriciaContext, func()) {
+func noopCtxFactory(context.Context) (PatriciaContext, func()) {
 	return &noopPatriciaContext{}, nil
 }
 
@@ -89,7 +89,7 @@ func (g *gatedPatriciaContext) TxNum() uint64                                 {
 // batch resets while the rest run fast, so the producer's arena reset races its in-flight reads.
 func slowCtxFactory(stall time.Duration) TrieContextFactory {
 	var n atomic.Int32
-	return func() (PatriciaContext, func()) {
+	return func(context.Context) (PatriciaContext, func()) {
 		if n.Add(1) == 1 {
 			return &gatedPatriciaContext{sleep: stall, descend: true}, nil
 		}
@@ -100,7 +100,7 @@ func slowCtxFactory(stall time.Duration) TrieContextFactory {
 // gatedCtxFactory returns a factory whose contexts signal entered then block on
 // release inside Branch, for deterministic single-worker ordering tests.
 func gatedCtxFactory(entered, release chan struct{}) TrieContextFactory {
-	return func() (PatriciaContext, func()) {
+	return func(context.Context) (PatriciaContext, func()) {
 		return &gatedPatriciaContext{entered: entered, release: release}, nil
 	}
 }
@@ -218,7 +218,7 @@ func TestHashSort_WarmupLap(t *testing.T) {
 // first key) while every other worker runs fast, so exactly one ring slot stays occupied.
 func gatedStragglerFactory(entered, release chan struct{}) TrieContextFactory {
 	var n atomic.Int32
-	return func() (PatriciaContext, func()) {
+	return func(context.Context) (PatriciaContext, func()) {
 		if n.Add(1) == 1 {
 			return &gatedPatriciaContext{entered: entered, release: release}, nil
 		}
```

### execution/commitment/commitmentdb/commitment_context.go
```diff
@@ -561,13 +561,15 @@ func (sdc *SharedDomainsCommitmentContext) ComputeCommitment(ctx context.Context
 			// Each worker writes its branch updates through a private collector
 			// so concurrent PutBranch calls never race; collectors are drained
 			// after Process and merged into the main writer below.
-			warmupConfig.CtxFactory, drainCollectors = sdc.concurrentTrieContextFactory(ctx, sdc.paraTrieDB, workerPin, txNum)
-			trie.SetTrieContextFactory(warmupConfig.CtxFactory)
+			var concurrentFactory commitment.TrieContextFactory
+			concurrentFactory, drainCollectors = sdc.concurrentTrieContextFactory(sdc.paraTrieDB, workerPin, txNum)
+			warmupConfig.CtxFactory = concurrentFactory
+			trie.SetTrieContextFactory(concurrentFactory)
 		default:
 			// Serial: this factory only serves page-cache warmup, which does not
 			// compute the root, so its reads need no generation pin. (Streaming is
 			// a *ParallelPatriciaHashed and takes the pinned branch above.)
-			warmupConfig.CtxFactory = sdc.trieContextFactory(ctx, sdc.paraTrieDB, txNum)
+			warmupConfig.CtxFactory = sdc.warmupTrieContextFactory(sdc.paraTrieDB, txNum)
 		}
 	}
 
@@ -664,10 +666,13 @@ func beginWorkerRo(ctx context.Context, db kv.TemporalRoDB, pin kv.TemporalFiles
 	return db.BeginTemporalRo(ctx)
 }
 
-func (sdc *SharedDomainsCommitmentContext) trieContextFactory(ctx context.Context, db kv.TemporalRoDB, txNum uint64) commitment.TrieContextFactory {
+func (sdc *SharedDomainsCommitmentContext) warmupTrieContextFactory(db kv.TemporalRoDB, txNum uint64) commitment.TrieContextFactory {
 	// avoid races like this
 	stepSize := sdc.sharedDomains.StepSize()
-	return func() (commitment.PatriciaContext, func()) {
+	return func(ctx context.Context) (commitment.PatriciaContext, func()) {
+		// Warmup is best-effort: never queue on the read-tx semaphore. A blocking
+		// acquire here can starve execution workers of slots and stall shutdown.
+		ctx = kv.WithNonBlockingAcquire(ctx)
 		roTx, err := db.BeginTemporalRo(ctx) //nolint:gocritic
 		if err != nil {
 			return &errorTrieContext{err: err}, func() {}
@@ -700,15 +705,15 @@ func (sdc *SharedDomainsCommitmentContext) trieContextFactory(ctx context.Contex
 	}
 }
 
-// concurrentTrieContextFactory is like trieContextFactory but also creates a per-goroutine
+// concurrentTrieContextFactory is like warmupTrieContextFactory but blocking, and also creates a per-goroutine
 // etl.Collector for each context so that PutBranch writes are isolated (no shared writer race).
 // Returns the factory and a drain function that collects all created collectors.
-func (sdc *SharedDomainsCommitmentContext) concurrentTrieContextFactory(ctx context.Context, db kv.TemporalRoDB, pin kv.TemporalFilesPin, txNum uint64) (commitment.TrieContextFactory, func() []*etl.Collector) {
+func (sdc *SharedDomainsCommitmentContext) concurrentTrieContextFactory(db kv.TemporalRoDB, pin kv.TemporalFilesPin, txNum uint64) (commitment.TrieContextFactory, func() []*etl.Collector) {
 	stepSize := sdc.sharedDomains.StepSize()
 	var mu sync.Mutex
 	var collectors []*etl.Collector
 
-	factory := func() (commitment.PatriciaContext, func()) {
+	factory := func(ctx context.Context) (commitment.PatriciaContext, func()) {
 		roTx, err := beginWorkerRo(ctx, db, pin) //nolint:gocritic
 		if err != nil {
 			return &errorTrieContext{err: err}, func() {}
```

### execution/commitment/commitmentdb/warmup_factory_test.go
```diff
@@ -0,0 +1,97 @@
+// Copyright 2026 The Erigon Authors
+// This file is part of Erigon.
+//
+// Erigon is free software: you can redistribute it and/or modify
+// it under the terms of the GNU Lesser General Public License as published by
+// the Free Software Foundation, either version 3 of the License, or
+// (at your option) any later version.
+//
+// Erigon is distributed in the hope that it will be useful,
+// but WITHOUT ANY WARRANTY; without even the implied warranty of
+// MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
+// GNU Lesser General Public License for more details.
+//
+// You should have received a copy of the GNU Lesser General Public License
+// along with Erigon. If not, see <http://www.gnu.org/licenses/>.
+
+package commitmentdb
+
+import (
+	"context"
+	"testing"
+	"time"
+
+	"github.com/stretchr/testify/require"
+
+	"github.com/erigontech/erigon/db/kv"
+	"github.com/erigontech/erigon/execution/commitment"
+)
+
+type stubSharedDomains struct{ sd }
+
+func (stubSharedDomains) StepSize() uint64 { return 1 }
+
+type beginRoRecordingDB struct {
+	kv.TemporalRoDB
+	sawNonBlocking bool
+}
+
+func (db *beginRoRecordingDB) BeginTemporalRo(ctx context.Context) (kv.TemporalTx, error) {
+	db.sawNonBlocking = kv.IsNonBlockingAcquire(ctx)
+	return nil, kv.ErrReadTxLimitExceeded
+}
+
+// Warmup is best-effort: its read txs must never queue on the read-tx
+// semaphore, or warmup workers can wedge commitment shutdown and starve
+// execution workers of semaphore slots.
+func TestWarmupTrieContextFactoryUsesNonBlockingReadTxAcquire(t *testing.T) {
+	t.Parallel()
+	db := &beginRoRecordingDB{}
+	sdc := &SharedDomainsCommitmentContext{sharedDomains: stubSharedDomains{}}
+
+	_, cleanup := sdc.warmupTrieContextFactory(db, 0)(t.Context())
+	defer cleanup()
+
+	require.True(t, db.sawNonBlocking, "warmup BeginTemporalRo must use non-blocking semaphore acquire")
+}
+
+type blockingBeginDB struct {
+	kv.TemporalRoDB
+}
+
+func (db *blockingBeginDB) BeginTemporalRo(ctx context.Context) (kv.TemporalTx, error) {
+	<-ctx.Done()
+	return nil, ctx.Err()
+}
+
+// A factory blocked opening its read tx (e.g. parked on the read-tx semaphore)
+// must unblock when the warmuper shuts down, or CloseAndWait hangs.
+func TestWarmupFactoriesUnblockBeginOnWarmuperClose(t *testing.T) {
+	t.Parallel()
+	sdc := &SharedDomainsCommitmentContext{sharedDomains: stubSharedDomains{}}
+	concurrent, _ := sdc.concurrentTrieContextFactory(&blockingBeginDB{}, nil, 0)
+	factories := map[string]commitment.TrieContextFactory{
+		"warmup":     sdc.warmupTrieContextFactory(&blockingBeginDB{}, 0),
+		"concurrent": concurrent,
+	}
+	for name, factory := range factories {
+		t.Run(name, func(t *testing.T) {
+			t.Parallel()
+			ctx, cancel := context.WithCancel(t.Context())
+			errCh := make(chan error, 1)
+			go func() {
+				trieCtx, cleanup := factory(ctx)
+				defer cleanup()
+				_, err := trieCtx.Account(nil)
+				errCh <- err
+			}()
+			cancel()
+			select {
+			case err := <-errCh:
+				require.ErrorIs(t, err, context.Canceled)
+			case <-time.After(10 * time.Second):
+				t.Fatal("factory did not honor warmuper ctx cancellation")
+			}
+		})
+	}
+}
```

### execution/commitment/nibble_addr_test.go
```diff
@@ -20,6 +20,7 @@
 package commitment
 
 import (
+	"context"
 	"encoding/binary"
 	"encoding/hex"
 	"fmt"
@@ -126,7 +127,7 @@ func findAddressForHexPrefix(nibblePrefix []byte, seed int) []byte {
 // mockTrieCtxFactory returns a TrieContextFactory that always returns the
 // given MockState and a no-op cleanup.
 func mockTrieCtxFactory(ms *MockState) TrieContextFactory {
-	return func() (PatriciaContext, func()) {
+	return func(context.Context) (PatriciaContext, func()) {
 		return ms, func() {}
 	}
 }
```

### execution/commitment/parallel_mount.go
```diff
@@ -84,7 +84,7 @@ func (p *ParallelPatriciaHashed) processMounted(ctx context.Context, updates *Up
 		return nil, fmt.Errorf("processMounted: nil template")
 	}
 	if base.ctx == nil && p.trieCtxFactory != nil {
-		bctx, cleanup := p.trieCtxFactory()
+		bctx, cleanup := p.trieCtxFactory(ctx)
 		if cleanup != nil {
 			defer cleanup()
 		}
@@ -134,7 +134,7 @@ func (p *ParallelPatriciaHashed) processMounted(ctx context.Context, updates *Up
 			} else {
 				w.traceW = nil
 			}
-			wctx, cleanup := p.trieCtxFactory()
+			wctx, cleanup := p.trieCtxFactory(gctx)
 			if cleanup != nil {
 				defer cleanup()
 			}
@@ -247,12 +247,12 @@ func printMountTiming(tStart, tUnfolded, tWorkers time.Time, buildDur, foldDur *
 	}
 }
 
-func (p *ParallelPatriciaHashed) newStorageWorker() (*HexPatriciaHashed, func()) {
+func (p *ParallelPatriciaHashed) newStorageWorker(ctx context.Context) (*HexPatriciaHashed, func()) {
 	var traceW io.Writer
 	if p.template != nil {
 		traceW = p.template.traceW
 	}
-	return newDeferredStorageWorker(&p.workerPool, p.trieCtxFactory, traceW)
+	return newDeferredStorageWorker(ctx, &p.workerPool, p.trieCtxFactory, traceW)
 }
 
 // setAccountStorageRoot writes the folded storage-root cell sr onto the account leaf.
```

### execution/commitment/parallel_patricia_hashed.go
```diff
@@ -338,7 +338,7 @@ func (p *ParallelPatriciaHashed) Process(
 		p.deferredForCaller = pu.deferredCombined
 		pu.deferredCombined = nil
 		pu.deferredMu.Unlock()
-	} else if aErr := p.applyDeferredUpdates(pu); aErr != nil {
+	} else if aErr := p.applyDeferredUpdates(ctx, pu); aErr != nil {
 		return nil, aErr
 	}
 
@@ -381,7 +381,7 @@ func dfsSubtree(node *prefixNode, path []byte, fn func(hashedKey, plainKey []byt
 }
 
 // applyDeferredUpdates applies the merged deferred branch updates, returning every entry to the pool on success or failure.
-func (p *ParallelPatriciaHashed) applyDeferredUpdates(pu *parallelUpdate) error {
+func (p *ParallelPatriciaHashed) applyDeferredUpdates(ctx context.Context, pu *parallelUpdate) error {
 	pu.deferredMu.Lock()
 	deferred := pu.deferredCombined
 	pu.deferredCombined = nil
@@ -396,7 +396,7 @@ func (p *ParallelPatriciaHashed) applyDeferredUpdates(pu *parallelUpdate) error
 		}
 	}()
 
-	applyCtx, cleanup := p.trieCtxFactory()
+	applyCtx, cleanup := p.trieCtxFactory(ctx)
 	if cleanup != nil {
 		defer cleanup()
 	}
```

### execution/commitment/parallel_patricia_hashed_test.go
```diff
@@ -86,14 +86,14 @@ func TestParallelPatriciaHashedSkeletonPlumbing(t *testing.T) {
 
 		ms := NewMockState(t)
 		called := 0
-		f := func() (PatriciaContext, func()) {
+		f := func(context.Context) (PatriciaContext, func()) {
 			called++
 			return ms, func() {}
 		}
 		p.SetTrieContextFactory(f)
 		require.NotNil(t, p.trieCtxFactory)
 
-		got, cleanup := p.trieCtxFactory()
+		got, cleanup := p.trieCtxFactory(context.Background())
 		assert.Same(t, ms, got)
 		assert.NotNil(t, cleanup)
 		assert.Equal(t, 1, called)
```

### execution/commitment/prepare_on_touch_test.go
```diff
@@ -23,7 +23,7 @@ type preparedSplits struct {
 func newPreparedSplits(t testing.TB, factory TrieContextFactory) *preparedSplits {
 	t.Helper()
 	base := NewHexPatriciaHashed(length.Addr, nil, DefaultTrieConfig())
-	bctx, bclean := factory()
+	bctx, bclean := factory(context.Background())
 	base.ResetContext(bctx)
 	base.branchEncoder.setDeferUpdates(true)
 	base.SetLeaveDeferredForCaller(true)
@@ -38,7 +38,7 @@ func newPreparedSplits(t testing.TB, factory TrieContextFactory) *preparedSplits
 	for i := range 16 {
 		w := NewHexPatriciaHashed(length.Addr, nil, DefaultTrieConfig())
 		w.mountTo(base, i)
-		wctx, wclean := factory()
+		wctx, wclean := factory(context.Background())
 		w.ResetContext(wctx)
 		w.branchEncoder.setDeferUpdates(true)
 		w.SetLeaveDeferredForCaller(true)
```
