# [?] Fix backfill retry panic when blob/column setup fails after block verification (#17235)

## Summary
Severity: Unknown
Chain: Ethereum
Component: prysmaticlabs/prysm
Published: 2026-09-11
Source: https://github.com/OffchainLabs/prysm/commit/e7c2be4fae5f3f6f973d120fec61e7395d1186af
Type: security-commit

## Details
Fix backfill retry panic when blob/column setup fails after block verification (#17235)

**What type of PR is this?**

Bug fix

**What does this PR do? Why is it needed?**

- handleBlocks sets b.blocks before newBlobSync/newColumnSync run, so a
construction error (e.g. CustodyGroupCount failure) leaves a retryable
batch with b.columns == nil, and the router's retry path panics in
transitionToNext dereferencing it.
- Route such batches back to batchSequenced for a full rebuild;
regression test included.

**Which issue(s) does this PR fix?**

Fixes #

**Other notes for review**

**Acknowledgements**

- [ ] I have read
[CONTRIBUTING.md](https://github.com/prysmaticlabs/prysm/blob/develop/CONTRIBUTING.md).
- [ ] I have included a uniquely named [changelog fragment
file](https://github.com/prysmaticlabs/prysm/blob/develop/CONTRIBUTING.md#maintaining-changelogmd).
- [ ] I have added a description with sufficient context for reviewers
to understand this PR.
- [ ] I have tested that my changes work as expected and I added a
testing plan to the PR description (if applicable).

---------

Co-authored-by: Kasey Kirkham <kasey@users.noreply.github.com>

## Patch
### beacon-chain/sync/backfill/batch.go
```diff
@@ -164,10 +164,10 @@ func (b batch) transitionToNext() batch {
 	if len(b.blocks) == 0 {
 		return b.withState(batchSequenced)
 	}
-	if len(b.columns.columnsNeeded()) > 0 {
+	if len(b.columnsNeeded()) > 0 {
 		return b.withState(batchSyncColumns)
 	}
-	if b.blobs != nil && b.blobs.needed() > 0 {
+	if b.blobsNeeded() > 0 {
 		return b.withState(batchSyncBlobs)
 	}
 	return b.withState(batchImportable)
```

### beacon-chain/sync/backfill/batch_test.go
```diff
@@ -5,6 +5,7 @@ import (
 	"testing"
 	"time"
 
+	"github.com/OffchainLabs/prysm/v7/beacon-chain/das"
 	"github.com/OffchainLabs/prysm/v7/consensus-types/primitives"
 	"github.com/OffchainLabs/prysm/v7/testing/require"
 	"github.com/pkg/errors"
@@ -110,6 +111,22 @@ func TestSortBatchDesc(t *testing.T) {
 	}
 }
 
+// TestRetryAfterSetupFailure covers handleBlocks failing after b.blocks is set but before
+// b.columns is constructed (e.g. a newColumnSync error): the router's retry path
+// (resetToRetryColumns -> transitionToNext) must rebuild the batch from batchSequenced
+// rather than dereference the nil columnSync.
+func TestRetryAfterSetupFailure(t *testing.T) {
+	expErr := errors.New("newColumnSync failed")
+	b := batch{state: batchSequenced, blocks: verifiedROBlocks{}}.withRetryableError(expErr)
+	b = resetToRetryColumns(b, das.CurrentNeeds{})
+	require.Equal(t, batchSequenced, b.state)
+
+	// Repeat for a nil blocks value
+	b = batch{state: batchSequenced, blocks: nil}.withRetryableError(expErr)
+	b = resetToRetryColumns(b, das.CurrentNeeds{})
+	require.Equal(t, batchSequenced, b.state)
+}
+
 func TestWaitUntilReady(t *testing.T) {
 	wur := batchBlockUntil
 
```

### beacon-chain/sync/backfill/blobs.go
```diff
@@ -62,6 +62,13 @@ type blobSync struct {
 	peer     peer.ID
 }
 
+func (b batch) blobsNeeded() int {
+	if b.blobs == nil {
+		return 0
+	}
+	return b.blobs.needed()
+}
+
 func (bs *blobSync) needed() int {
 	return len(bs.expected) - bs.next
 }
```

### beacon-chain/sync/backfill/columns.go
```diff
@@ -110,12 +110,12 @@ type columnSync struct {
 	bisector *columnBisector
 }
 
-func newColumnSync(ctx context.Context, b batch, blks verifiedROBlocks, current primitives.Slot, p p2p.P2P, cfg *workerCfg) (*columnSync, error) {
+func newColumnSync(ctx context.Context, begin, end primitives.Slot, blks verifiedROBlocks, current primitives.Slot, p p2p.P2P, cfg *workerCfg) (*columnSync, error) {
 	cgc, err := p.CustodyGroupCount(ctx)
 	if err != nil {
 		return nil, errors.Wrap(err, "custody group count")
 	}
-	cb, err := buildColumnBatch(ctx, b, blks, p, cfg.colStore, cfg.currentNeeds())
+	cb, err := buildColumnBatch(ctx, begin, end, blks, p, cfg.colStore, cfg.currentNeeds())
 	if err != nil {
 		return nil, err
 	}
@@ -143,6 +143,13 @@ func (cs *columnSync) blockColumns(root [32]byte) *toDownload {
 	return cs.columnBatch.toDownload[root]
 }
 
+func (b batch) columnsNeeded() peerdas.ColumnIndices {
+	if b.columns == nil {
+		return peerdas.ColumnIndices{}
+	}
+	return b.columns.needed()
+}
+
 func (cs *columnSync) columnsNeeded() peerdas.ColumnIndices {
 	if cs.columnBatch == nil {
 		return peerdas.ColumnIndices{}
@@ -261,12 +268,12 @@ func currentCustodiedColumns(ctx context.Context, p p2p.P2P) (peerdas.ColumnIndi
 	return peerdas.NewColumnIndicesFromMap(peerInfo.CustodyColumns), nil
 }
 
-func buildColumnBatch(ctx context.Context, b batch, blks verifiedROBlocks, p p2p.P2P, store *filesystem.DataColumnStorage, needs das.CurrentNeeds) (*columnBatch, error) {
+func buildColumnBatch(ctx context.Context, begin, end primitives.Slot, blks verifiedROBlocks, p p2p.P2P, store *filesystem.DataColumnStorage, needs das.CurrentNeeds) (*columnBatch, error) {
 	if len(blks) == 0 {
 		return nil, nil
 	}
 
-	if !needs.Col.At(b.begin) && !needs.Col.At(b.end-1) {
+	if !needs.Col.At(begin) && !needs.Col.At(end-1) {
 		return nil, nil
 	}
 
```

### beacon-chain/sync/backfill/columns_test.go
```diff
@@ -354,7 +354,7 @@ func TestBuildColumnBatch(t *testing.T) {
 		p := p2ptest.NewTestP2P(t)
 		store := filesystem.NewEphemeralDataColumnStorage(t)
 
-		cb, err := buildColumnBatch(ctx, batch{}, verifiedROBlocks{}, p, store, specNeeds)
+		cb, err := buildColumnBatch(ctx, 0, 0, verifiedROBlocks{}, p, store, specNeeds)
 		require.NoError(t, err)
 		nilIshColumnBatch(t, cb)
 	})
@@ -371,7 +371,7 @@ func TestBuildColumnBatch(t *testing.T) {
 			end:   denebSlot + 10,
 		}
 
-		cb, err := buildColumnBatch(ctx, b, blks, p, store, specNeeds)
+		cb, err := buildColumnBatch(ctx, b.begin, b.end, blks, p, store, specNeeds)
 		require.NoError(t, err)
 		nilIshColumnBatch(t, cb)
 	})
@@ -388,7 +388,7 @@ func TestBuildColumnBatch(t *testing.T) {
 			end:   fuluSlot + 10,
 		}
 
-		cb, err := buildColumnBatch(ctx, b, blks, p, store, specNeeds)
+		cb, err := buildColumnBatch(ctx, b.begin, b.end, blks, p, store, specNeeds)
 		require.NoError(t, err)
 		nilIshColumnBatch(t, cb)
 	})
@@ -405,7 +405,7 @@ func TestBuildColumnBatch(t *testing.T) {
 			end:   fuluSlot,
 		}
 
-		cb, err := buildColumnBatch(ctx, b, blks, p, store, specNeeds)
+		cb, err := buildColumnBatch(ctx, b.begin, b.end, blks, p, store, specNeeds)
 		require.NoError(t, err)
 		require.NotNil(t, cb, "batch at Fulu boundary should not be nil")
 	})
@@ -422,7 +422,7 @@ func TestBuildColumnBatch(t *testing.T) {
 			end:   fuluSlot + 1,
 		}
 
-		cb, err := buildColumnBatch(ctx, b, blks, p, store, specNeeds)
+		cb, err := buildColumnBatch(ctx, b.begin, b.end, blks, p, store, specNeeds)
 		require.NoError(t, err)
 		require.NotNil(t, cb, "last block at Fulu boundary should not be nil")
 	})
@@ -438,7 +438,7 @@ func TestBuildColumnBatch(t *testing.T) {
 			end:   fuluSlot,
 		}
 
-		cb, err := buildColumnBatch(ctx, b, blks, p, store, specNeeds)
+		cb, err := buildColumnBatch(ctx, b.begin, b.end, blks, p, store, specNeeds)
 		require.NoError(t, err)
 		nilIshColumnBatch(t, cb)
 	})
@@ -464,7 +464,7 @@ func TestBuildColumnBatch(t *testing.T) {
 			end:   fuluSlot + primitives.Slot(postFuluCount),
 		}
 
-		cb, err := buildColumnBatch(ctx, b, allBlocks, p, store, specNeeds)
+		cb, err := buildColumnBatch(ctx, b.begin, b.end, allBlocks, p, store, specNeeds)
 		require.NoError(t, err)
 		require.NotNil(t, cb, "mixed epoch batch should not be nil")
 		// Should only include Fulu blocks
@@ -483,7 +483,7 @@ func TestBuildColumnBatch(t *testing.T) {
 			end:   fuluSlot + 100,
 		}
 
-		cb, err := buildColumnBatch(ctx, b, blks, p, store, specNeeds)
+		cb, err := buildColumnBatch(ctx, b.begin, b.end, blks, p, store, specNeeds)
 		require.NoError(t, err)
 		require.NotNil(t, cb, "first block at Fulu should not be nil")
 		require.Equal(t, 3, len(cb.toDownload), "should include all 3 blocks")
@@ -500,7 +500,7 @@ func TestBuildColumnBatch(t *testing.T) {
 			end:   fuluSlot + 10,
 		}
 
-		cb, err := buildColumnBatch(ctx, b, blks, p, store, specNeeds)
+		cb, err := buildColumnBatch(ctx, b.begin, b.end, blks, p, store, specNeeds)
 		require.NoError(t, err)
 		require.NotNil(t, cb)
 		require.Equal(t, fuluSlot, cb.first, "first slot should be set")
@@ -519,7 +519,7 @@ func TestBuildColumnBatch(t *testing.T) {
 			end:   fuluSlot + 10,
 		}
 
-		cb, err := buildColumnBatch(ctx, b, blks, p, store, specNeeds)
+		cb, err := buildColumnBatch(ctx, b.begin, b.end, blks, p, store, specNeeds)
 		require.NoError(t, err)
 		require.NotNil(t, cb)
 		require.Equal(t, fuluSlot, cb.first, "first should be slot of first block with commitments")
@@ -549,7 +549,7 @@ func TestBuildColumnBatch(t *testing.T) {
 			end:   fuluSlot + 10,
 		}
 
-		cb, err := buildColumnBatch(ctx, b, allBlocks, p, store, specNeeds)
+		cb, err := buildColumnBatch(ctx, b.begin, b.end, allBlocks, p, store, specNeeds)
 		require.NoError(t, err)
 		require.NotNil(t, cb)
 		// Should only have 2 blocks (those with commitments)
@@ -934,7 +934,7 @@ func TestNewColumnSync(t *testing.T) {
 		}
 
 		// Empty blocks should result in nil columnBatch
-		cs, err := newColumnSync(ctx, batch{}, verifiedROBlocks{}, current, p2p, cfg)
+		cs, err := newColumnSync(ctx, 0, 0, verifiedROBlocks{}, current, p2p, cfg)
 		require.NoError(t, err)
 		require.NotNil(t, cs, "columnSync should not be nil")
 		require.Equal(t, true, cs.columnBatch == nil, "columnBatch should be nil for empty blocks")
@@ -946,21 +946,15 @@ func TestNewColumnSync(t *testing.T) {
 		colStore := filesystem.NewEphemeralDataColumnStorage(t)
 		current := fuluSlot + 100
 
-		blks, _ := testBlobGen(t, fuluSlot, 2)
-		b := batch{
-			begin:  fuluSlot,
-			end:    fuluSlot + 10,
-			blocks: blks,
-		}
-
 		cfg := &workerCfg{
 			colStore:     colStore,
 			downscore:    func(peer.ID, string, error) {},
 			currentNeeds: func() das.CurrentNeeds { return mockCurrentSpecNeeds() },
 		}
-
-		cs, err := newColumnSync(ctx, b, blks, current, p2p, cfg)
+		blks, _ := testBlobGen(t, fuluSlot, 2)
+		cs, err := newColumnSync(ctx, fuluSlot, fuluSlot+10, blks, current, p2p, cfg)
 		require.NoError(t, err)
+
 		require.NotNil(t, cs)
 		require.NotNil(t, cs.columnBatch, "columnBatch should be initialized")
 		require.NotNil(t, cs.store, "store should be initialized")
```

### beacon-chain/sync/backfill/worker.go
```diff
@@ -151,17 +151,21 @@ func (w *p2pWorker) handleBlocks(ctx context.Context, b batch) batch {
 	}
 	blockDownloadBytesApprox.Add(float64(bdl))
 	log.WithFields(b.logFields()).WithField("bytesDownloaded", bdl).Trace("Blocks downloaded")
-	b.blocks = verified
 
 	bscfg := &blobSyncConfig{currentNeeds: w.cfg.currentNeeds, nbv: w.cfg.newVB, store: w.cfg.blobStore}
 	bs, err := newBlobSync(current, verified, bscfg)
 	if err != nil {
 		return b.withRetryableError(err)
 	}
-	cs, err := newColumnSync(ctx, b, verified, current, w.p2p, w.cfg)
+	cs, err := newColumnSync(ctx, b.begin, b.end, verified, current, w.p2p, w.cfg)
 	if err != nil {
 		return b.withRetryableError(err)
 	}
+
+	// Update the batch with the verified blocks, blob sync, and column sync
+	// before transitioning to the next state. Note that if we experience any failures
+	// in newBlobSync or newColumnSync, we'll start the whole batch from scratch for simplicity.
+	b.blocks = verified
 	b.blobs = bs
 	b.columns = cs
 	return b.transitionToNext()
```

### changelog/satushh_backfill-setup-retry-panic.md
```diff
@@ -0,0 +1,3 @@
+### Fixed
+
+- Fixed a nil-pointer panic in the backfill worker pool when retrying a batch whose blob/column sync construction failed after block verification (e.g. a `CustodyGroupCount` error in `newColumnSync`).
```
