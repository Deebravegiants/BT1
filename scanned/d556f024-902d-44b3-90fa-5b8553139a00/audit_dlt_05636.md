# [?] stagedsync, db: fix TxLookup prune crash with membatch cursor during FCU (#20122)

## Summary
Severity: Unknown
Chain: Ethereum
Component: erigontech/erigon
Published: 2026-03-24
Source: https://github.com/erigontech/erigon/commit/cabda2a61f6783250d1cd192fa5e299097fabdf5
Type: security-commit

## Details
stagedsync, db: fix TxLookup prune crash with membatch cursor during FCU (#20122)

## Summary

- During FCU, the pipeline runs on a `membatchwithdb.MemoryMutation`
(block overlay). The TxLookup prune stage's type switch only handled
`*mdbx.MdbxCursor`, causing a crash when it received
`*memoryMutationCursor`:
  ```
unexpected cursor type *membatchwithdb.memoryMutationCursor for table
BlockTransactionLookup
  ```
- Adds a generic `kv.RwCursorPseudoDupSort` wrapper that makes any
`RwCursor` satisfy `PseudoDupSortRwCursor` for non-DupSort tables (same
semantics as the existing MDBX-specific wrapper)
- Applied the same defensive fix to domain and history prune type
switches

Observed on blob-devnet-0 at block 327898 ([slot
424431](https://dora.blob-devnet-0.ethpandaops.io/slot/424431)).

## Test plan

- [ ] Verify on blob-devnet-0 that FCU no longer crashes at the TxLookup
prune stage
- [ ] `make lint` passes
- [ ] `make test-short` passes

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-authored-by: Claude Opus 4.6 (1M context) <noreply@anthropic.com>

## Patch
### db/kv/kv_interface.go
```diff
@@ -310,6 +310,37 @@ type PseudoDupSortRwCursor interface { // For both DupSort and usual cursors (us
 	CountDuplicates() (uint64, error) // CountDuplicates - number of duplicates for the current key
 }
 
+// RwCursorPseudoDupSort wraps any RwCursor to satisfy PseudoDupSortRwCursor
+// for non-DupSort tables. Each key has exactly one value, so dup operations
+// are trivial: CountDuplicates returns 1, NextDup returns nil, etc.
+type RwCursorPseudoDupSort struct {
+	RwCursor
+}
+
+func (c *RwCursorPseudoDupSort) DeleteExact(k1, k2 []byte) error {
+	return c.Delete(k1)
+}
+func (c *RwCursorPseudoDupSort) NextNoDup() ([]byte, []byte, error) {
+	return c.Next()
+}
+func (c *RwCursorPseudoDupSort) NextDup() ([]byte, []byte, error) {
+	return nil, nil, nil
+}
+func (c *RwCursorPseudoDupSort) FirstDup() ([]byte, error) {
+	_, v, err := c.Current()
+	return v, err
+}
+func (c *RwCursorPseudoDupSort) LastDup() ([]byte, error) {
+	_, v, err := c.Current()
+	return v, err
+}
+func (c *RwCursorPseudoDupSort) DeleteCurrentDuplicates() error {
+	return c.DeleteCurrent()
+}
+func (c *RwCursorPseudoDupSort) CountDuplicates() (uint64, error) {
+	return 1, nil
+}
+
 const Unlim int = -1 // const Unbounded/EOF/EndOfTable []byte = nil
 
 type StatelessRwTx interface {
```

### db/state/domain.go
```diff
@@ -1943,7 +1943,7 @@ func (dt *DomainRoTx) prune(ctx context.Context, rwTx kv.RwTx, step kv.Step, txF
 		case *mdbx2.MdbxDupSortCursor:
 			valsCursor = valsRwCursor.(*mdbx2.MdbxDupSortCursor)
 		default:
-			return stat, fmt.Errorf("unexpected cursor type %T for table %s", valsRwCursor, dt.d.ValuesTable)
+			valsCursor = &kv.RwCursorPseudoDupSort{RwCursor: c}
 		}
 		defer valsCursor.Close()
 	} else {
```

### db/state/history.go
```diff
@@ -1107,7 +1107,7 @@ func (ht *HistoryRoTx) prune(ctx context.Context, rwTx kv.RwTx, txFrom, txTo, li
 		case *mdbx2.MdbxDupSortCursor:
 			valsCP = valsC.(*mdbx2.MdbxDupSortCursor)
 		default:
-			return nil, fmt.Errorf("unexpected cursor type %T for table %s", valsC, ht.h.ValuesTable)
+			valsCP = &kv.RwCursorPseudoDupSort{RwCursor: c}
 		}
 	}
 
@@ -1172,7 +1172,7 @@ func (ht *HistoryRoTx) oldPrune(ctx context.Context, rwTx kv.RwTx, txFrom, txTo,
 		case *mdbx2.MdbxDupSortCursor:
 			valsCP = valsC.(*mdbx2.MdbxDupSortCursor)
 		default:
-			return nil, fmt.Errorf("unexpected cursor type %T for table %s", valsC, ht.h.ValuesTable)
+			valsCP = &kv.RwCursorPseudoDupSort{RwCursor: c}
 		}
 	}
 
```

### execution/stagedsync/stage_txlookup.go
```diff
@@ -265,7 +265,7 @@ func PruneTxLookup(s *PruneState, tx kv.RwTx, cfg TxLookupCfg, ctx context.Conte
 	case *mdbx2.MdbxCursor:
 		valsCursor = &mdbx2.MdbxCursorPseudoDupSort{MdbxCursor: c}
 	default:
-		return fmt.Errorf("unexpected cursor type %T for table %s", valsRwCursor, kv.TxLookup)
+		valsCursor = &kv.RwCursorPseudoDupSort{RwCursor: c}
 	}
 
 	logEvery := time.NewTicker(logInterval)
```
