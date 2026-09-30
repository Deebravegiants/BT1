# [?] fix(chainindex): fix nil deref in recompute closure and handle large reconciliation gaps (#13552)

## Summary
Severity: Unknown
Chain: Filecoin
Component: filecoin-project/lotus
Published: 2026-03-31
Source: https://github.com/filecoin-project/lotus/commit/8f8f62269b342a2ec369ab224e621d0982eb84e8
Type: security-commit

## Details
fix(chainindex): fix nil deref in recompute closure and handle large reconciliation gaps (#13552)

* fix(chainindex): fix nil deref in recompute closure and handle large reconciliation gaps

1. Fix nil pointer dereference in loadExecutedMessages where the recompute
   closure captured the outer err variable by reference.

2. When the chain index is too far behind chain head (beyond
   MaxReconcileTipsets), reconciliation would attempt a massive single-
   transaction backfill causing "database is locked" failures and preventing
   node startup. Detect the gap early and enter a degraded mode where reads
   return ErrBackfillRequired but ChainValidateIndex and Apply/Revert still
   function.

## Patch
### CHANGELOG.md
```diff
@@ -26,6 +26,7 @@
 - fix(api): `StateSearchMsg` should respect `lookbackLimit` [filecoin-project/lotus#13562](https://github.com/filecoin-project/lotus/pull/13562)
 - fix(ecfinality): account for null rounds in EC finality calculator chain walk, aligning with FRC-0089 theoretical model and fixing depth-to-height conversion ([filecoin-project/lotus#13565](https://github.com/filecoin-project/lotus/pull/13565))
 - fix(eth): tighten block range handling for `trace_filter` and `eth_getLogs`, including consistent `-32005` limit-exceeded errors and gateway range enforcement for `trace_filter` ([filecoin-project/lotus#13561](https://github.com/filecoin-project/lotus/pull/13561))
+- fix(chainindex): fix nil deref during event backfill and handle large index-to-chain gaps during startup reconciliation by entering a degraded mode instead of blocking with a long-held SQLite transaction ([filecoin-project/lotus#13552](https://github.com/filecoin-project/lotus/pull/13552))
 
 # Node and Miner v1.35.0 / 2026-02-19
 
```

### chain/index/events.go
```diff
@@ -161,13 +161,13 @@ func loadExecutedMessages(ctx context.Context, cs ChainStore, recomputeTipSetSta
 	st := cs.ActorStore(ctx)
 
 	var recomputed bool
-	recompute := func() error {
+	recompute := func(loadErr error) error {
 		tskCid, err2 := rctTs.Key().Cid()
 		if err2 != nil {
 			return xerrors.Errorf("failed to compute tipset key cid: %w", err2)
 		}
 
-		log.Warnf("failed to load receipts for tipset %s (height %d): %s; recomputing tipset state", tskCid.String(), rctTs.Height(), err.Error())
+		log.Warnf("failed to load receipts for tipset %s (height %d): %s; recomputing tipset state", tskCid.String(), rctTs.Height(), loadErr.Error())
 		if err := recomputeTipSetStateFunc(ctx, msgTs); err != nil {
 			return xerrors.Errorf("failed to recompute tipset state: %w", err)
 		}
@@ -181,7 +181,7 @@ func loadExecutedMessages(ctx context.Context, cs ChainStore, recomputeTipSetSta
 			return nil, xerrors.Errorf("failed to load message receipts: %w", err)
 		}
 
-		if err := recompute(); err != nil {
+		if err := recompute(err); err != nil {
 			return nil, err
 		}
 		recomputed = true
@@ -219,7 +219,7 @@ func loadExecutedMessages(ctx context.Context, cs ChainStore, recomputeTipSetSta
 				return nil, xerrors.Errorf("failed to load events root for message %s: err: %w", ems[i].msg.Cid(), err)
 			}
 			// we may have the receipts but not the events, IsStoringEvents may have been false
-			if err := recompute(); err != nil {
+			if err := recompute(err); err != nil {
 				return nil, err
 			}
 			eventsArr, err = amt4.LoadAMT(ctx, st, *rct.EventsRoot, amt4.UseTreeBitWidth(types.EventAMTBitwidth))
@@ -398,8 +398,13 @@ func (si *SqliteIndexer) getTipsetKeyCidByHeight(ctx context.Context, height abi
 // GetEventsForFilter returns matching events for the given filter
 // Returns nil, nil if the filter has no matching events
 // Returns nil, ErrNotFound if the filter has no matching events and the tipset is not indexed
+// Returns nil, ErrBackfillRequired if the index is in degraded mode and requires a backfill
 // Returns nil, err for all other errors
 func (si *SqliteIndexer) GetEventsForFilter(ctx context.Context, f *EventFilter) ([]*CollectedEvent, error) {
+	if si.needsBackfill {
+		return nil, ErrBackfillRequired
+	}
+
 	getEventsFnc := func(stmt *sql.Stmt, values []any) ([]*CollectedEvent, error) {
 		q, err := stmt.QueryContext(ctx, values...)
 		if err != nil {
```

### chain/index/indexer.go
```diff
@@ -80,7 +80,8 @@ type SqliteIndexer struct {
 	updateSubs   map[uint64]*updateSub
 	subIdCounter uint64
 
-	started bool
+	started       bool
+	needsBackfill bool
 
 	// ensures writes are serialized so backfilling does not race with index updates
 	writerLk sync.Mutex
```

### chain/index/interface.go
```diff
@@ -18,6 +18,7 @@ import (
 
 var ErrNotFound = errors.New("not found in index")
 var ErrClosed = errors.New("index closed")
+var ErrBackfillRequired = errors.New("chain index requires backfill")
 
 // MsgInfo is the Message metadata the index tracks.
 type MsgInfo struct {
```

### chain/index/read.go
```diff
@@ -19,6 +19,9 @@ func (si *SqliteIndexer) GetCidFromHash(ctx context.Context, txHash ethtypes.Eth
 	if si.isClosed() {
 		return cid.Undef, ErrClosed
 	}
+	if si.needsBackfill {
+		return cid.Undef, ErrBackfillRequired
+	}
 
 	var msgCidBytes []byte
 
@@ -44,6 +47,9 @@ func (si *SqliteIndexer) GetMsgInfo(ctx context.Context, messageCid cid.Cid) (*M
 	if si.isClosed() {
 		return nil, ErrClosed
 	}
+	if si.needsBackfill {
+		return nil, ErrBackfillRequired
+	}
 
 	var tipsetKeyCidBytes []byte
 	var height int64
```

### chain/index/reconcile.go
```diff
@@ -73,6 +73,7 @@ func (si *SqliteIndexer) ReconcileWithChain(ctx context.Context, head *types.Tip
 		// we only need to walk back as far as the reconciliation epoch as all the tipsets in the index
 		// below the reconciliation epoch are already marked as reverted because the reconciliation epoch
 		// is the minimum non-reverted height in the index
+		epochsWalked := abi.ChainEpoch(0)
 		for currTs != nil && currTs.Height() >= reconciliationEpoch {
 			tsKeyCidBytes, err := toTipsetKeyCidBytes(currTs)
 			if err != nil {
@@ -92,6 +93,17 @@ func (si *SqliteIndexer) ReconcileWithChain(ctx context.Context, head *types.Tip
 				break
 			}
 
+			epochsWalked++
+			if si.maxReconcileTipsets > 0 && uint64(epochsWalked) >= si.maxReconcileTipsets {
+				si.needsBackfill = true
+				return xerrors.Errorf("gap between chain index and chain head is too large (walked %d epochs without "+
+					"finding a matching tipset, MaxReconcileTipsets is %d); to start the node in a degraded mode and "+
+					"backfill the index, set AllowIndexReconciliationFailure to true in the [ChainIndexer] config, "+
+					"then use 'lotus index validate-backfill' (or the ChainValidateIndex RPC) to repair the index "+
+					"and restart: %w",
+					epochsWalked, si.maxReconcileTipsets, ErrBackfillRequired)
+			}
+
 			if currTs.Height() == 0 {
 				log.Infof("ReconcileWithChain reached genesis but no matching tipset found in index")
 				break
@@ -142,6 +154,7 @@ func (si *SqliteIndexer) ReconcileWithChain(ctx context.Context, head *types.Tip
 
 		return nil
 	})
+
 }
 
 func (si *SqliteIndexer) getReconciliationEpoch(ctx context.Context, tx *sql.Tx) (abi.ChainEpoch, error) {
```

### chain/index/reconcile_test.go
```diff
@@ -0,0 +1,144 @@
+package index
+
+import (
+	"context"
+	"errors"
+	pseudo "math/rand"
+	"testing"
+	"time"
+
+	"github.com/ipfs/go-cid"
+	"github.com/stretchr/testify/require"
+
+	"github.com/filecoin-project/go-address"
+	"github.com/filecoin-project/go-state-types/abi"
+
+	"github.com/filecoin-project/lotus/chain/types"
+	"github.com/filecoin-project/lotus/chain/types/ethtypes"
+)
+
+func TestReconcileGapTooLarge(t *testing.T) {
+	ctx := context.Background()
+	seed := time.Now().UnixNano()
+	t.Logf("seed: %d", seed)
+	rng := pseudo.New(pseudo.NewSource(seed))
+
+	// Index has data at height 100 but chain head is far ahead. Build a chain
+	// where GetTipSetFromKey works for walking backwards from head.
+	maxReconcile := uint64(50) // small value for testing
+	indexedHeight := abi.ChainEpoch(100)
+	headHeight := indexedHeight + abi.ChainEpoch(maxReconcile) + 100
+
+	cs := newDummyChainStore()
+
+	// Build a chain of tipsets from genesis up to headHeight so the backwards
+	// walk in ReconcileWithChain can resolve parents.
+	tipsets := make(map[abi.ChainEpoch]*types.TipSet)
+	var parentCids []cid.Cid
+	for h := abi.ChainEpoch(0); h <= headHeight; h++ {
+		ts := fakeTipSet(t, rng, h, parentCids)
+		tipsets[h] = ts
+		cs.SetTipsetByHeightAndKey(h, ts.Key(), ts)
+		parentCids = ts.Key().Cids()
+	}
+
+	head := tipsets[headHeight]
+	cs.SetHeaviestTipSet(head)
+
+	// Create the indexer with maxReconcileTipsets set to the small value so
+	// the backwards walk triggers the gap limit.
+	si, err := NewSqliteIndexer(":memory:", cs, 0, false, maxReconcile)
+	require.NoError(t, err)
+	t.Cleanup(func() { _ = si.Close() })
+
+	insertHead(t, si, tipsets[indexedHeight], indexedHeight)
+
+	// ReconcileWithChain should detect the gap exceeds MaxReconciliationGap
+	// and return ErrBackfillRequired.
+	err = si.ReconcileWithChain(ctx, head)
+	require.Error(t, err)
+	require.True(t, errors.Is(err, ErrBackfillRequired), "expected ErrBackfillRequired, got: %v", err)
+}
+
+func TestReconcileSmallGapSucceeds(t *testing.T) {
+	ctx := context.Background()
+	seed := time.Now().UnixNano()
+	t.Logf("seed: %d", seed)
+	rng := pseudo.New(pseudo.NewSource(seed))
+
+	// Gap within the limit should succeed.
+	indexedHeight := abi.ChainEpoch(100)
+	headHeight := indexedHeight + 10
+
+	cs := newDummyChainStore()
+
+	tipsets := make(map[abi.ChainEpoch]*types.TipSet)
+	var parentCids []cid.Cid
+	for h := abi.ChainEpoch(0); h <= headHeight; h++ {
+		ts := fakeTipSet(t, rng, h, parentCids)
+		tipsets[h] = ts
+		cs.SetTipsetByHeightAndKey(h, ts.Key(), ts)
+		parentCids = ts.Key().Cids()
+	}
+
+	head := tipsets[headHeight]
+	cs.SetHeaviestTipSet(head)
+
+	si, err := NewSqliteIndexer(":memory:", cs, 0, false, 10000)
+	require.NoError(t, err)
+	t.Cleanup(func() { _ = si.Close() })
+
+	insertHead(t, si, tipsets[indexedHeight], indexedHeight)
+
+	si.SetActorToDelegatedAddresFunc(func(ctx context.Context, emitter abi.ActorID, ts *types.TipSet) (address.Address, bool) {
+		idAddr, err := address.NewIDAddress(uint64(emitter))
+		if err != nil {
+			return address.Undef, false
+		}
+		return idAddr, true
+	})
+
+	// Set up a no-op messages loader since backfill will try to index tipsets
+	si.setExecutedMessagesLoaderFunc(func(ctx context.Context, cs ChainStore, msgTs, rctTs *types.TipSet) ([]executedMessage, error) {
+		return nil, nil
+	})
+
+	err = si.ReconcileWithChain(ctx, head)
+	require.NoError(t, err)
+}
+
+func TestBackfillRequiredDegradedMode(t *testing.T) {
+	ctx := context.Background()
+	seed := time.Now().UnixNano()
+	t.Logf("seed: %d", seed)
+	rng := pseudo.New(pseudo.NewSource(seed))
+
+	headHeight := abi.ChainEpoch(100)
+	si, _, _ := setupWithHeadIndexed(t, headHeight, rng)
+	t.Cleanup(func() { _ = si.Close() })
+	si.Start()
+
+	// Reads should work before setting backfill required
+	_, err := si.GetMsgInfo(ctx, randomCid(t, rng))
+	require.True(t, errors.Is(err, ErrNotFound), "expected ErrNotFound from empty index, got: %v", err)
+
+	_, err = si.GetCidFromHash(ctx, ethtypes.EthHash{})
+	require.True(t, errors.Is(err, ErrNotFound), "expected ErrNotFound from empty index, got: %v", err)
+
+	// Simulate degraded mode (set by ReconcileWithChain when gap is too large)
+	si.needsBackfill = true
+
+	// Read methods should return ErrBackfillRequired
+	_, err = si.GetMsgInfo(ctx, randomCid(t, rng))
+	require.True(t, errors.Is(err, ErrBackfillRequired), "expected ErrBackfillRequired, got: %v", err)
+
+	_, err = si.GetCidFromHash(ctx, ethtypes.EthHash{})
+	require.True(t, errors.Is(err, ErrBackfillRequired), "expected ErrBackfillRequired, got: %v", err)
+
+	_, err = si.GetEventsForFilter(ctx, &EventFilter{MinHeight: 1, MaxHeight: 50})
+	require.True(t, errors.Is(err, ErrBackfillRequired), "expected ErrBackfillRequired, got: %v", err)
+
+	// ChainValidateIndex should still work (this is the backfill path)
+	_, err = si.ChainValidateIndex(ctx, 50, false)
+	require.False(t, errors.Is(err, ErrBackfillRequired), "ChainValidateIndex should not return ErrBackfillRequired, got: %v", err)
+}
```

### node/modules/chainindex.go
```diff
@@ -102,8 +102,9 @@ func InitChainIndexer(cfg config.ChainIndexerConfig) func(lc fx.Lifecycle, mctx
 						return xerrors.Errorf("error while reconciling chain index with chain state: %w", err)
 					}
 					log.Warnf("error while reconciling chain index with chain state: %s", err)
+				} else {
+					unlockObserver()
 				}
-				unlockObserver()
 
 				indexer.Start()
 
```
