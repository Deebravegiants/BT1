# [?] stagedsync, membatchwithdb: fix data race in parallel executor overlay (#20036)

## Summary
Severity: Unknown
Chain: Ethereum
Component: erigontech/erigon
Published: 2026-03-20
Source: https://github.com/erigontech/erigon/commit/5c8ab95f073a348a6f4d744e3489f1dc261222c6
Type: security-commit

## Details
stagedsync, membatchwithdb: fix data race in parallel executor overlay (#20036)

## Summary

- Fix data race between executor and apply goroutines in the parallel
executor's `MemoryMutation` overlay path
- Add `OverlayTemporalReadView` — a `kv.TemporalTx` implementation that
gives each goroutine its own MDBX RO tx while sharing the in-memory
overlay
- Add `ForEach` to `OverlayReadView` to prevent overlay bypass (same
class of bug as `ForAmount`)
- Fix silent `Seek` error swallowing in `ForEach`/`ForAmount` on both
`MemoryMutation` and `OverlayReadView`

## Problem

When `rwTx` is a `MemoryMutation` (the overlay path from #19882), the
parallel executor shared the same object between the executor and apply
goroutines:

```go
case kv.TemporalTx:
    asyncTx = applyTx  // both goroutines share same MdbxTx
```

Both goroutines create/close cursors on the shared underlying `MdbxTx`,
racing on `toCloseMap` (a plain `map[uint64]kv.Closer`) and mdbx cursor
internals. This caused 18+ race-test failures on `bal-devnet-3`,
triggered by `experimentalBAL: true` changing execution timing.

## Fix

`OverlayTemporalReadView` wraps a caller-provided `kv.TemporalTx`
(independent RO tx) and merges reads with the `MemoryMutation`'s shared
in-memory layer — same approach as the existing `OverlayReadView` used
by engine server getters.

```go
case *membatchwithdb.MemoryMutation:
    execRoTx, _ := pe.cfg.db.BeginTemporalRo(ctx)
    defer execRoTx.Rollback()
    asyncTx = applyTx.NewTemporalReadView(execRoTx)
```

Key properties preserved from #19882:
- No MDBX write lock during pipeline (RO tx only)
- Cross-call overlay persistence (shared in-memory layer)
- No OS-thread affinity

### Additional fixes

- **`OverlayReadView.ForEach` added**: Without this, `ForEach` calls
fell through to the embedded `kv.Tx`, completely bypassing the in-memory
overlay — same class of bug that `ForAmount` had.
- **`Seek` error handling**: In `ForEach`/`ForAmount` on both
`MemoryMutation` and `OverlayReadView`, the initial `c.Seek()` error was
silently swallowed when `k == nil` (error checked only inside the loop
body, which never executed). Extracted `Seek` into a separate statement
with explicit error check.

## Test plan

- [x] `make erigon` builds
- [x] `make lint` passes (2 runs)
- [x] `go test ./db/kv/membatchwithdb/...` passes
- [x] `go test -race` passes for all previously failing tests:
`TestDump`, `TestFeeHistory`, `TestSuggestPrice`,
`TestSuggestTipCap_SparseBlocks`, plus 13 `rpc/jsonrpc` tests
- [ ] CI race-tests/core-rpc

🤖 Generated with [Claude Code](https://claude.com/claude-code)

---------

Co-authored-by: Claude Opus 4.6 (1M context) <noreply@anthropic.com>

### db/kv/membatchwithdb/memory_mutation.go
```diff
@@ -194,7 +194,11 @@ func (m *MemoryMutation) ForAmount(bucket string, prefix []byte, amount uint32,
 	}
 	defer c.Close()
 
-	for k, v, err := c.Seek(prefix); k != nil && amount > 0; k, v, err = c.Next() {
+	k, v, err := c.Seek(prefix)
+	if err != nil {
+		return err
+	}
+	for ; k != nil && amount > 0; k, v, err = c.Next() {
 		if err != nil {
 			return err
 		}
@@ -301,7 +305,11 @@ func (m *MemoryMutation) ForEach(bucket string, fromPrefix []byte, walker func(k
 	}
 	defer c.Close()
 
-	for k, v, err := c.Seek(fromPrefix); k != nil; k, v, err = c.Next() {
+	k, v, err := c.Seek(fromPrefix)
+	if err != nil {
+		return err
+	}
+	for ; k != nil; k, v, err = c.Next() {
 		if err != nil {
 			return err
 		}
@@ -1013,6 +1021,125 @@ func (v *OverlayReadView) makeCursor(bucket string) (kv.CursorDupSort, error) {
 	return c, err
 }
 
+func (v *OverlayReadView) ForEach(bucket string, fromPrefix []byte, walker func(k, v []byte) error) error {
+	c, err := v.Cursor(bucket)
+	if err != nil {
+		return err
+	}
+	defer c.Close()
+
+	k, val, err := c.Seek(fromPrefix)
+	if err != nil {
+		return err
+	}
+	for ; k != nil; k, val, err = c.Next() {
+		if err != nil {
+			return err
+		}
+		if err := walker(k, val); err != nil {
+			return err
+		}
+	}
+	return nil
+}
+
+func (v *OverlayReadView) ForAmount(bucket string, prefix []byte, amount uint32, walker func(k, val []byte) error) error {
+	if amount == 0 {
+		return nil
+	}
+	c, err := v.Cursor(bucket)
+	if err != nil {
+		return err
+	}
+	defer c.Close()
+
+	k, val, err := c.Seek(prefix)
+	if err != nil {
+		return err
+	}
+	for ; k != nil && amount > 0; k, val, err = c.Next() {
+		if err != nil {
+			return err
+		}
+		if err := walker(k, val); err != nil {
+			return err
+		}
+		amount--
+	}
+	return nil
+}
+
+// OverlayTemporalReadView extends OverlayReadView with kv.TemporalTx support.
+// It embeds OverlayReadView for all overlay-aware KV methods (GetOne, Cursor,
+// etc.) and delegates temporal methods (GetLatest, GetAsOf, etc.) to its own
+// independent temporal tx.
+//
+// Use NewTemporalReadView to create one. The caller is responsible for rolling
+// back the underlying temporalTx when done.
+type OverlayTemporalReadView struct {
+	*OverlayReadView
+	temporalTx kv.TemporalTx
+}
+
+var _ kv.TemporalTx = (*OverlayTemporalReadView)(nil)
+
+// NewTemporalReadView creates a temporal read-only view that checks the overlay's
+// mem layer first, then falls back to temporalTx for DB reads. The temporalTx
+// must be a fresh, independently-opened transaction — it is NOT shared with the
+// overlay's internal backing tx.
+func (m *MemoryMutation) NewTemporalReadView(temporalTx kv.TemporalTx) *OverlayTemporalReadView {
+	return &OverlayTemporalReadView{
+		OverlayReadView: m.NewReadView(temporalTx),
+		temporalTx:      temporalTx,
+	}
+}
+
+func (v *OverlayTemporalReadView) Apply(_ context.Context, f func(tx kv.Tx) error) error {
+	return f(v)
+}
+
+// Temporal methods — delegate to the independent temporal tx.
+
+func (v *OverlayTemporalReadView) GetLatest(name kv.Domain, k []byte) ([]byte, kv.Step, error) {
+	return v.temporalTx.GetLatest(name, k)
+}
+func (v *OverlayTemporalReadView) HasPrefix(name kv.Domain, prefix []byte) ([]byte, []byte, bool, error) {
+	return v.temporalTx.HasPrefix(name, prefix)
+}
+func (v *OverlayTemporalReadView) StepsInFiles(entitySet ...kv.Domain) kv.Step {
+	return v.temporalTx.StepsInFiles(entitySet...)
+}
+func (v *OverlayTemporalReadView) GetAsOf(name kv.Domain, k []byte, ts uint64) ([]byte, bool, error) {
+	return v.temporalTx.GetAsOf(name, k, ts)
+}
+func (v *OverlayTemporalReadView) RangeAsOf(name kv.Domain, fromKey, toKey []byte, ts uint64, asc order.By, limit int) (stream.KV, error) {
+	return v.temporalTx.RangeAsOf(name, fromKey, toKey, ts, asc, limit)
+}
+func (v *OverlayTemporalReadView) IndexRange(name kv.InvertedIdx, k []byte, fromTs, toTs int, asc order.By, limit int) (stream.U64, error) {
+	return v.temporalTx.IndexRange(name, k, fromTs, toTs, asc, limit)
+}
+func (v *OverlayTemporalReadView) HistorySeek(name kv.Domain, k []byte, ts uint64) ([]byte, bool, error) {
+	return v.temporalTx.HistorySeek(name, k, ts)
+}
+func (v *OverlayTemporalReadView) HistoryRange(name kv.Domain, fromTs, toTs int, asc order.By, limit int) (stream.KV, error) {
+	return v.temporalTx.HistoryRange(name, fromTs, toTs, asc, limit)
+}
+func (v *OverlayTemporalReadView) Debug() kv.TemporalDebugTx {
+	return v.temporalTx.Debug()
+}
+func (v *OverlayTemporalReadView) AggTx() any {
+	return v.temporalTx.AggTx()
+}
+func (v *OverlayTemporalReadView) AggForkablesTx(id kv.ForkableId) any {
+	return v.temporalTx.AggForkablesTx(id)
+}
+func (v *OverlayTemporalReadView) Unmarked(id kv.ForkableId) kv.UnmarkedTx {
+	return v.temporalTx.Unmarked(id)
+}
+func (v *OverlayTemporalReadView) FreezeInfo() kv.FreezeInfo {
+	return v.temporalTx.FreezeInfo()
+}
+
 type temporaldb struct {
 	memoryMutation *MemoryMutation
 }
```

### execution/stagedsync/exec3_parallel.go
```diff
@@ -22,6 +22,7 @@ import (
 	"github.com/erigontech/erigon/db/datadir"
 	"github.com/erigontech/erigon/db/kv"
 	"github.com/erigontech/erigon/db/kv/mdbx"
+	"github.com/erigontech/erigon/db/kv/membatchwithdb"
 	"github.com/erigontech/erigon/db/kv/temporal"
 	"github.com/erigontech/erigon/db/state/changeset"
 	"github.com/erigontech/erigon/diagnostics/metrics"
@@ -115,10 +116,19 @@ func (pe *parallelExecutor) exec(ctx context.Context, execStage *StageState, u U
 		temporalTx := applyTx.AsyncClone(mdbx.NewAsyncRwTx(applyTx.RwTx, 1000))
 		asyncTxChan = temporalTx.ApplyChan()
 		asyncTx = temporalTx
-	case kv.TemporalTx:
-		// MemoryMutation overlay — pure Go, no thread affinity.
-		// No asyncTx needed; exec goroutine reads directly from the overlay.
-		asyncTx = applyTx
+	case *membatchwithdb.MemoryMutation:
+		// MemoryMutation overlay — pure Go, no thread affinity for the in-memory
+		// layer. However, cursor operations on the underlying MdbxTx are NOT
+		// thread-safe. Create an OverlayTemporalReadView with its own independent
+		// RO tx for the executor goroutine, so it doesn't share MDBX cursors
+		// with the apply goroutine. The overlay's in-memory data is still shared
+		// (protected by MemoryMutation's RWMutex).
+		execRoTx, err := pe.cfg.db.BeginTemporalRo(ctx)
+		if err != nil {
+			return nil, rwTx, fmt.Errorf("open RO tx for executor overlay: %w", err)
+		}
+		defer execRoTx.Rollback()
+		asyncTx = applyTx.NewTemporalReadView(execRoTx)
 	default:
 		return nil, rwTx, fmt.Errorf("expected *temporal.RwTx: got %T", rwTx)
 	}
```
