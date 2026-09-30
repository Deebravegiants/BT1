# [?] core, blockstm, state, docs: harden valuesEqual, recover validation panic, split settleNonces/settleStorage, document tx lifecycle

## Summary
Severity: Unknown
Chain: Polygon
Component: maticnetwork/bor
Published: 2026-05-13
Source: https://github.com/0xPolygon/bor/commit/6cbd6ffbe3a1dcf862c3172e381958de18b5f1f1
Type: security-commit

## Details
core, blockstm, state, docs: harden valuesEqual, recover validation panic, split settleNonces/settleStorage, document tx lifecycle

- core/state/parallel_statedb_validate.go: replace `default: a == b` in
  valuesEqual with an explicit type switch over the MVStore value types
  in use (bool, uint64, common.Hash, []byte, nil). Unknown types now
  panic with a clear message instead of either silently degrading to
  pointer-identity (for pointer types) or crashing the runtime (for
  non-comparable types like slices, maps, or structs containing them) —
  both of which would be consensus-affecting failure modes the moment a
  new MVStore subpath is added.

- core/blockstm/v2_executor.go: wrap runValidationLoop's body in a
  defer-recover so a panic in Validate() is captured into
  V2ExecutionResult.ValidationPanic instead of crashing the bor process
  via an unrecovered goroutine panic. A second deferred close on
  chSettle (guarded by settleClosed) keeps the settle goroutine from
  hanging on wg.Wait when the recover path skips the normal cleanup.
  core/parallel_state_processor.go: surface a non-nil ValidationPanic
  as an error so BlockChain.ProcessBlock falls back to the serial
  processor instead of taking down the node.

- core/state/parallel_statedb_settle.go: split settleNoncesAndStorage
  into settleNonces and settleStorage. The two loops were independent
  with no shared state or ordering constraint; bundling them was
  inconsistent with the rest of the per-concern settle helpers. Test
  TestPDB_SettleNoncesAndStorage splits in lockstep.

- docs/blockstm-v2.md: add a Transaction Lifecycle section between
  Execution Flow and Key data structures. Covers (1) the state diagram
  a tx passes through, (2) the structural invariant that bounds each
  tx to at most two executions (validation order + the
  finishReexec(i-1) gate + no re-validation of the re-exec result),
  (3) a worked cascading-vfail example walking tx1/tx2/tx3 through
  initial+reexec to show why a 3-tx cascade still converges with one
  re-exec per failed tx, and (4) a concurrency timeline diagram
  illustrating the worker/validator/reexec/settle lanes. Also reorders
  the Storage/Nonces bullets in the Settlement section to match
  SettleTo's call order.

Tests added: TestValuesEqual_Bool, TestValuesEqual_Nil,
TestValuesEqual_UnsupportedTypePanics (lock in the loud-panic
contract), and TestV2ValidationPanicIsRecovered (end-to-end check that
a panicking Validate() surfaces via ValidationPanic without hanging
the executor).

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>

### core/blockstm/v2_executor.go
```diff
@@ -2,11 +2,13 @@ package blockstm
 
 import (
 	"context"
+	"runtime/debug"
 	"sync"
 	"sync/atomic"
 	"time"
 
 	"github.com/ethereum/go-ethereum/common"
+	"github.com/ethereum/go-ethereum/log"
 )
 
 // ---------------------------------------------------------------------------
@@ -86,6 +88,9 @@ type V2ExecutionResult struct {
 	ValWaitDur  time.Duration // time waiting for workers
 	ValCheckDur time.Duration // time doing validation checks
 	ValReexDur  time.Duration // time blocked on re-execution
+	// Non-nil if runValidationLoop recovered from a panic; caller should
+	// discard this result and fall back to serial.
+	ValidationPanic any
 }
 
 // ExecuteV2BlockSTM runs transactions with pipelined parallel execution.
@@ -161,6 +166,8 @@ type v2ExecCtx struct {
 	valWaitDur  time.Duration
 	valCheckDur time.Duration
 	valReexDur  time.Duration
+
+	validationPanic any // non-nil if runValidationLoop recovered from a panic
 }
 
 func newV2ExecCtx(tasks []V2Task, env V2Env, coinbase common.Address,
@@ -624,6 +631,23 @@ func (x *v2ExecCtx) validateOne(reexecDone []chan struct{}, i int) bool {
 // toPrev or vfailed[i-1]). After the main loop, it drains any leftovers.
 func (x *v2ExecCtx) runValidationLoop(valDone chan struct{}) {
 	defer close(valDone)
+
+	// Defer order (LIFO): recover runs first to capture the panic, then
+	// chSettle is closed so the settle goroutine drains even on panic.
+	settleClosed := false
+	defer func() {
+		if x.chSettle != nil && !settleClosed {
+			close(x.chSettle)
+		}
+	}()
+	defer func() {
+		if r := recover(); r != nil {
+			x.validationPanic = r
+			log.Error("V2 validation panic — falling back to serial",
+				"err", r, "stack", string(debug.Stack()))
+		}
+	}()
+
 	reexecDone := make([]chan struct{}, x.n)
 	cancelled := false
 	for i := 0; i < x.n; i++ {
@@ -652,6 +676,7 @@ func (x *v2ExecCtx) runValidationLoop(valDone chan struct{}) {
 	// drain. Closing chSettle terminates the settlement goroutine.
 	if x.chSettle != nil {
 		close(x.chSettle)
+		settleClosed = true
 	}
 }
 
@@ -669,16 +694,17 @@ func (x *v2ExecCtx) buildResult(startTime time.Time, settleStart, settleEnd *tim
 		sd = settleEnd.Sub(*settleStart)
 	}
 	return &V2ExecutionResult{
-		States:      x.states,
-		ExecCount:   int(x.execCount.Load()),
-		VFailCount:  int(x.vfailCount.Load()),
-		VFailCats:   x.vfailCats,
-		VFailIdxs:   x.vfailIdxs,
-		Phase1:      phase1Dur,
-		BaseOnly:    baseOnly,
-		SettleDur:   sd,
-		ValWaitDur:  x.valWaitDur,
-		ValCheckDur: x.valCheckDur,
-		ValReexDur:  x.valReexDur,
+		States:          x.states,
+		ExecCount:       int(x.execCount.Load()),
+		VFailCount:      int(x.vfailCount.Load()),
+		VFailCats:       x.vfailCats,
+		VFailIdxs:       x.vfailIdxs,
+		Phase1:          phase1Dur,
+		BaseOnly:        baseOnly,
+		SettleDur:       sd,
+		ValWaitDur:      x.valWaitDur,
+		ValCheckDur:     x.valCheckDur,
+		ValReexDur:      x.valReexDur,
+		ValidationPanic: x.validationPanic,
 	}
 }
```

### core/blockstm/v2_executor_test.go
```diff
@@ -37,9 +37,9 @@ func (s *mockV2State) SetDeferMVWrites(bool)                   {}
 
 type mockV2Task struct{ idx int }
 
-func (t *mockV2Task) Index() int                  { return t.idx }
-func (t *mockV2Task) Sender() common.Address      { return common.Address{} }
-func (t *mockV2Task) To() *common.Address         { return nil }
+func (t *mockV2Task) Index() int                    { return t.idx }
+func (t *mockV2Task) Sender() common.Address        { return common.Address{} }
+func (t *mockV2Task) To() *common.Address           { return nil }
 func (t *mockV2Task) Authorities() []common.Address { return nil }
 
 type mockV2Env struct {
@@ -221,16 +221,58 @@ func TestV2ValidationLoopSerializationBlocksReexec(t *testing.T) {
 	}
 }
 
+type panickingV2State struct{}
+
+func (s *panickingV2State) Validate() bool                          { panic("synthetic validation panic") }
+func (s *panickingV2State) ValidateCategory() string                { return "" }
+func (s *panickingV2State) IsBaseOnly() bool                        { return false }
+func (s *panickingV2State) MarkEstimate()                           {}
+func (s *panickingV2State) CleanupEstimate([]Key, []common.Address) {}
+func (s *panickingV2State) GetWriteKeys() []Key                     { return nil }
+func (s *panickingV2State) GetBalAddrs() []common.Address           { return nil }
+func (s *panickingV2State) FlushToMVStore()                         {}
+func (s *panickingV2State) SetDeferMVWrites(bool)                   {}
+
+type panickingV2Env struct{ s *panickingV2State }
+
+func (e *panickingV2Env) BaseNonce(common.Address) uint64 { return 0 }
+func (e *panickingV2Env) Execute(task V2Task, workerID int, incarnation int,
+	senderNonces map[common.Address]uint64, coinbase common.Address,
+	waitForTx func(int), waitForFinal func(int), deferWrites bool) V2TxState {
+	return e.s
+}
+func (e *panickingV2Env) Recycle(V2TxState) {}
+
+// TestV2ValidationPanicIsRecovered: a panic in Validate() must surface
+// via ValidationPanic rather than crashing the process; settle goroutine
+// must still exit so ExecuteV2BlockSTM doesn't hang on wg.Wait.
+func TestV2ValidationPanicIsRecovered(t *testing.T) {
+	env := &panickingV2Env{s: &panickingV2State{}}
+	tasks := []V2Task{&mockV2Task{0}}
+	settleFn := func(int, V2TxState) {}
+
+	result := ExecuteV2BlockSTM(context.Background(), tasks, env, common.Address{}, 2, nil, settleFn)
+	if result == nil {
+		t.Fatal("expected non-nil result")
+	}
+	if result.ValidationPanic == nil {
+		t.Fatal("ValidationPanic must be non-nil")
+	}
+	if s, ok := result.ValidationPanic.(string); !ok || s != "synthetic validation panic" {
+		t.Errorf("ValidationPanic = %v, want sentinel string", result.ValidationPanic)
+	}
+}
+
 // nonceMockTask lets tests override Sender/Authorities per task.
 type nonceMockTask struct {
-	idx     int
-	sender  common.Address
-	auths   []common.Address
+	idx    int
+	sender common.Address
+	auths  []common.Address
 }
 
-func (t *nonceMockTask) Index() int                  { return t.idx }
-func (t *nonceMockTask) Sender() common.Address      { return t.sender }
-func (t *nonceMockTask) To() *common.Address         { return nil }
+func (t *nonceMockTask) Index() int                    { return t.idx }
+func (t *nonceMockTask) Sender() common.Address        { return t.sender }
+func (t *nonceMockTask) To() *common.Address           { return nil }
 func (t *nonceMockTask) Authorities() []common.Address { return t.auths }
 
 // nonceMockEnv reads BaseNonce from a per-address map.
```

### core/parallel_state_processor.go
```diff
@@ -1110,6 +1110,9 @@ func (p *V2StateProcessor) Process(block *types.Block, statedb *state.StateDB, c
 	if result.PanickedIdx >= 0 {
 		return nil, fmt.Errorf("v2: tx %d panicked during execution", result.PanickedIdx)
 	}
+	if result.ValidationPanic != nil {
+		return nil, fmt.Errorf("v2: validation panic: %v", result.ValidationPanic)
+	}
 	// Same logic for ApplyMessage consensus-level errors (bad nonce,
 	// insufficient upfront gas, intrinsic gas underflow, etc.). Serial returns
 	// the underlying error from state_processor.go:222 and aborts the block;
```

### core/state/parallel_statedb.go
```diff
@@ -1193,7 +1193,7 @@ func (s *ParallelStateDB) RecordTransfer(sender, recipient common.Address, amoun
 	return true
 }
 
-// SettleTo and its helpers (settleNoncesAndStorage, settleCode,
+// SettleTo and its helpers (settleNonces, settleStorage, settleCode,
 // settleBalanceOpsAndLogs, tryEmitTransferAt, emitTransferLog,
 // settleAccountSet, applyFeeData, GetLogs) live in
 // parallel_statedb_settle.go.
```

### core/state/parallel_statedb_coverage_test.go
```diff
@@ -762,7 +762,7 @@ func TestValuesEqual_Bytes(t *testing.T) {
 	}
 }
 
-// TestValuesEqual_Default compares non-byte values via ==.
+// TestValuesEqual_Default compares non-byte values via the typed switch.
 func TestValuesEqual_Default(t *testing.T) {
 	if !valuesEqual(uint64(5), uint64(5)) {
 		t.Fatal("equal uint64 must compare equal")
@@ -776,6 +776,46 @@ func TestValuesEqual_Default(t *testing.T) {
 	}
 }
 
+// TestValuesEqual_Bool covers the bool case (suicide/create subpaths).
+func TestValuesEqual_Bool(t *testing.T) {
+	if !valuesEqual(true, true) {
+		t.Fatal("equal bools must compare equal")
+	}
+	if valuesEqual(true, false) {
+		t.Fatal("different bools must not compare equal")
+	}
+	if valuesEqual(true, uint64(1)) {
+		t.Fatal("bool vs uint64 must not compare equal")
+	}
+}
+
+// TestValuesEqual_Nil covers nil-interface absence-read comparisons.
+func TestValuesEqual_Nil(t *testing.T) {
+	if !valuesEqual(nil, nil) {
+		t.Fatal("two nils must compare equal")
+	}
+	if valuesEqual(nil, uint64(0)) {
+		t.Fatal("nil vs typed zero must not compare equal")
+	}
+	if valuesEqual(uint64(0), nil) {
+		t.Fatal("typed zero vs nil must not compare equal")
+	}
+}
+
+// TestValuesEqual_UnsupportedTypePanics ensures the default branch panics
+// rather than silently calling interface{} == . A new MVStore value type
+// that doesn't get an explicit case must surface loudly in CI.
+func TestValuesEqual_UnsupportedTypePanics(t *testing.T) {
+	defer func() {
+		r := recover()
+		if r == nil {
+			t.Fatal("expected panic for unsupported value type")
+		}
+	}()
+	type unsupported struct{ x int }
+	valuesEqual(unsupported{1}, unsupported{1})
+}
+
 // ---------------------------------------------------------------------------
 // GetCodeHash branches
 // ---------------------------------------------------------------------------
```

### core/state/parallel_statedb_settle.go
```diff
@@ -20,7 +20,8 @@ func (s *ParallelStateDB) SettleTo(final *StateDB) {
 	// and uses that for the fee transfer log; we must match for parity.
 	preTxCoinbaseBal := final.GetBalance(s.Coinbase)
 
-	s.settleNoncesAndStorage(final)
+	s.settleNonces(final)
+	s.settleStorage(final)
 	s.settleCode(final)
 	s.settleBalanceOpsAndLogs(final)
 	s.settleAccountSet(final)
@@ -32,13 +33,17 @@ func (s *ParallelStateDB) SettleTo(final *StateDB) {
 	final.FinaliseFastWithPrefetch(true)
 }
 
-// settleNoncesAndStorage applies pending nonce and storage writes to final.
-func (s *ParallelStateDB) settleNoncesAndStorage(final *StateDB) {
+// settleNonces applies pending nonce writes to final.
+func (s *ParallelStateDB) settleNonces(final *StateDB) {
 	for addr, nonce := range s.localNonces {
 		final.SetNonceDirect(addr, nonce)
 	}
-	// Origins may be stale (from pathdb), but that only affects the skip
-	// optimization in commitStorage — which we've removed.
+}
+
+// settleStorage applies pending storage writes to final. Origins may be
+// stale (from pathdb), but that only affects the skip optimization in
+// commitStorage — which we've removed.
+func (s *ParallelStateDB) settleStorage(final *StateDB) {
 	for addr, slots := range s.localStorage {
 		origins := make(map[common.Hash]common.Hash, len(slots))
 		for key := range slots {
```

### core/state/parallel_statedb_test.go
```diff
@@ -789,22 +789,34 @@ func settleFinalDB(t *testing.T) *StateDB {
 	return pdb.rawBase.Copy()
 }
 
-// TestPDB_SettleNoncesAndStorage writes both nonce and storage into the
-// final StateDB and asserts they landed.
-func TestPDB_SettleNoncesAndStorage(t *testing.T) {
+// TestPDB_SettleNonces writes the tx's nonce changes into the final
+// StateDB.
+func TestPDB_SettleNonces(t *testing.T) {
 	pdb, _, _ := newTestPDB(t, 0)
 	final := settleFinalDB(t)
 	addr := common.HexToAddress("0xabcd")
-	slot := common.HexToHash("0x01")
 
 	pdb.SetNonce(addr, 7, tracing.NonceChangeUnspecified)
-	pdb.SetState(addr, slot, common.HexToHash("0xdead"))
 
-	pdb.settleNoncesAndStorage(final)
+	pdb.settleNonces(final)
 
 	if got := final.GetNonce(addr); got != 7 {
 		t.Fatalf("nonce: got %d, want 7", got)
 	}
+}
+
+// TestPDB_SettleStorage writes the tx's storage slot changes into the
+// final StateDB.
+func TestPDB_SettleStorage(t *testing.T) {
+	pdb, _, _ := newTestPDB(t, 0)
+	final := settleFinalDB(t)
+	addr := common.HexToAddress("0xabcd")
+	slot := common.HexToHash("0x01")
+
+	pdb.SetState(addr, slot, common.HexToHash("0xdead"))
+
+	pdb.settleStorage(final)
+
 	if got := final.GetState(addr, slot); got != common.HexToHash("0xdead") {
 		t.Fatalf("storage: got %s, want 0xdead", got.Hex())
 	}
```

### core/state/parallel_statedb_validate.go
```diff
@@ -1,26 +1,36 @@
 package state
 
 import (
+	"bytes"
+	"fmt"
+
 	"github.com/ethereum/go-ethereum/common"
 	"github.com/ethereum/go-ethereum/core/blockstm"
 )
 
-// valuesEqual compares two interface{} values safely (handles []byte).
+// valuesEqual compares MVStore reads/writes. New value types MUST add
+// a case — the default panics rather than falling back to interface{}
+// equality, which panics for non-comparable types (slices, maps) and
+// silently uses pointer-identity for pointer types.
 func valuesEqual(a, b interface{}) bool {
+	if a == nil || b == nil {
+		return a == b
+	}
 	switch av := a.(type) {
 	case []byte:
 		bv, ok := b.([]byte)
-		if !ok || len(av) != len(bv) {
-			return false
-		}
-		for i := range av {
-			if av[i] != bv[i] {
-				return false
-			}
-		}
-		return true
+		return ok && bytes.Equal(av, bv)
+	case common.Hash:
+		bv, ok := b.(common.Hash)
+		return ok && av == bv
+	case uint64:
+		bv, ok := b.(uint64)
+		return ok && av == bv
+	case bool:
+		bv, ok := b.(bool)
+		return ok && av == bv
 	default:
-		return a == b
+		panic(fmt.Sprintf("valuesEqual: unsupported MVStore value type %T", a))
 	}
 }
 
```

### docs/blockstm-v2.md
```diff
@@ -85,6 +85,106 @@ delivers roughly 1.6x speedup over the serial path
    `WaitForFinal(writerIdx)` until the upstream writer is finalized,
    then re-read.
 
+### Transaction Lifecycle
+
+Each transaction passes through one of two paths:
+
+```
+  Pending → Executing → Validating ─┬─ pass → Finalized → Settled
+                                    └─ fail → ReExecuting → Finalized → Settled
+```
+
+Workers run `Executing` for many txs in parallel; the single validator
+goroutine walks `Validating` in tx-index order; the single settle
+goroutine consumes `Finalized` txs in tx-index order.
+
+#### At most two executions per tx
+
+A transaction is executed at most **twice**: the initial speculative
+run, plus one re-execution if validation fails. The re-executed result
+is trusted by construction — there is no second `Validate()` call. Three
+load-bearing facts make this sound:
+
+1. **Validation runs in tx-index order.** `runValidationLoop` iterates
+   `i = 0..n-1` calling `validateOne(i)` (`v2_executor.go`).
+
+2. **Before validating tx i, all predecessors are finalized.**
+   `validateOne(i)` calls `finishReexec(reexecDone, i-1)`, which
+   blocks on `reexecDone[i-1]` until tx i-1's re-execution has flushed
+   its writes to MVStore. So by the time tx i's reads are checked,
+   every prior tx's writes are committed at their final incarnation.
+
+3. **The re-exec result is trusted, not re-validated.**
+   `finishReexec` marks `finalized[idx]=true` and pushes to settle
+   without calling `Validate()` again.
+
+Together: when tx i's re-execution runs, it sees a fully-stabilized
+predecessor history, so one re-exec converges. The build-tag-gated
+`assertReexecVisitedExactlyOnce` pins this at runtime — every
+dispatched re-exec is consumed exactly once.
+
+#### Worked example: a cascading dependency
+
+Three transactions where each depends on the previous:
+
+```
+tx1: writes slot A
+tx2: reads slot A, writes slot B (only on the correct branch)
+tx3: reads slot B
+```
+
+Phase 1 — parallel speculative execution:
+
+```
+tx1: writes A=newA                                [exec 1]
+tx2: races past tx1, reads A=baseA               [exec 1]
+     wrong branch → no write to B
+tx3: reads B (no writer found, records absence)  [exec 1]
+```
+
+Phase 2 — sequential validation:
+
+```
+validateOne(0): tx1's reads are clean       → finalizePass
+validateOne(1): tx2's recorded read of A
+                doesn't match the current
+                MVStore entry (now tx1's)    → dispatchReexec(1)
+                  tx2 reexec: reads A=newA,
+                  writes B=newB              [exec 2]
+validateOne(2): finishReexec(1) — blocks
+                  until tx2's reexec lands
+                tx3's recorded "no writer
+                for B" no longer matches
+                (tx2 now writes B)           → dispatchReexec(2)
+                  tx3 reexec: reads B=newB,
+                  runs correctly             [exec 2]
+```
+
+Total execution counts: tx1 = 1, tx2 = 2, tx3 = 2. No transaction
+reaches a third execution despite the cascading dependency. The
+property holds because each re-execution runs against a stable
+view — tx3's re-exec sees the final tx2 state, not a transient one,
+because `finishReexec(1)` completed before `validateOne(2)` proceeded
+to re-validate tx3's reads.
+
+This is also the scalability ceiling. Because each successor's
+re-exec waits for the predecessor's re-exec via `finishReexec(i-1)`,
+a chain of dependent re-executions serializes through this gate. The
+worker pool can churn through *initial* executions of later txs in
+parallel during these waits, but re-execs themselves serialize.
+
+#### Concurrency timeline (same cascade)
+
+```
+Workers:    [tx1_exec]──┐ [tx2_exec]──┐ [tx3_exec]──┐ ...
+                        │             │             │
+Validator:              └─validate(0) ┴─validate(1)─┴─validate(2)
+                                       ↓dispatch    ↓ wait(reexec1)
+                                       reexec1───→  ↓dispatch
+                                                    reexec2 ───→
+Settle:                  settle(0)     ...          settle(1)  settle(2)
+```
+
 ### Key data structures
 
 **`*state.ParallelStateDB`** (`core/state/parallel_statedb.go`).
@@ -149,12 +249,12 @@ Special cases:
 ### Settlement
 
 Each validated tx's writes hit `finalDB` via the `*Direct` setter
-family:
+family, in `SettleTo`'s call order:
 
+- **Nonces.** `SetNonceDirect` — bypass journal, mark dirty.
 - **Storage.** `SetStorageDirectWithOrigins` — bypasses journaling and
   pre-populates `originStorage` so `FinaliseFastWithPrefetch` doesn't
   go to disk for origin lookups.
-- **Nonces.** `SetNonceDirect` — bypass journal, mark dirty.
 - **Code.** `SetCode` (the journaled path; rare per-tx).
 - **Balances.** Replayed from the per-tx `BalanceOps` slice in order,
   interleaved with transfer-log emission so receipts and balance
```
