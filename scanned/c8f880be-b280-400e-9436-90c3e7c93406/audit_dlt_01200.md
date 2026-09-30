# [?] caplin: fix chain_reorg Server-Sent Event depth underflow and wrong old_head_block (#21440)

## Summary
Severity: Unknown
Chain: Ethereum
Component: erigontech/erigon
Published: 2026-06-04
Source: https://github.com/erigontech/erigon/commit/cfe582c7ff73be7d45bb4fd5965cab6ebf113f6e
Type: security-commit

## Details
caplin: fix chain_reorg Server-Sent Event depth underflow and wrong old_head_block (#21440)

## Summary
- **depth** was computed as `newHeadSlot - forkPoint`, which could
underflow to `2^64 - 2`; now correctly computed as `oldHeadSlot -
forkPoint`
- **old_head_block** contained the common ancestor root instead of the
previous canonical tip; now uses `ReadCanonicalHead` (`cursor.Last()`)
to capture the actual old tip before mutations
- **1-slot reorgs** were silently missed because the old `parentRoot !=
oldCanonical` check compared identical values; replaced with
`currentSlot < oldHeadSlot`

Fixes #20885

## Test plan
- [x] `TestUpdateCanonicalChainReorgEvent` — same-length 2-slot reorg
- [x] `TestUpdateCanonicalChainReorgShorterFork` — old chain longer than
new fork
- [x] `TestUpdateCanonicalChainReorgLongerFork` — new fork longer than
old chain
- [x] `TestUpdateCanonicalChainNoReorg` — normal chain extension (no
event emitted)
- [x] `TestUpdateCanonicalChainReorgOneSlot` — minimal 1-slot reorg
(depth=1)
- [x] `make erigon` builds
- [x] `golangci-lint` clean on changed packages

🤖 Generated with [Claude Code](https://claude.com/claude-code)

---------

Co-authored-by: Claude Opus 4.6 <noreply@anthropic.com>

## Patch
### cl/persistence/beacon_indicies/indicies.go
```diff
@@ -135,6 +135,24 @@ func ReadCanonicalBlockRoot(tx kv.Tx, slot uint64) (common.Hash, error) {
 	return blockRoot, nil
 }
 
+func ReadCanonicalHead(tx kv.Tx) (uint64, common.Hash, error) {
+	cursor, err := tx.Cursor(kv.CanonicalBlockRoots)
+	if err != nil {
+		return 0, common.Hash{}, err
+	}
+	defer cursor.Close()
+	k, v, err := cursor.Last()
+	if err != nil {
+		return 0, common.Hash{}, err
+	}
+	if k == nil {
+		return 0, common.Hash{}, nil
+	}
+	var root common.Hash
+	copy(root[:], v)
+	return base_encoding.Decode64FromBytes4(k), root, nil
+}
+
 func WriteLastBeaconSnapshot(tx kv.RwTx, slot uint64) error {
 	return tx.Put(kv.LastBeaconSnapshot, []byte(kv.LastBeaconSnapshotKey), base_encoding.Encode64ToBytes4(slot))
 }
```

### cl/persistence/beacon_indicies/indicies_test.go
```diff
@@ -127,6 +127,31 @@ func TestTruncateCanonicalChain(t *testing.T) {
 	require.Equal(t, common.Hash{}, canonicalRoot)
 }
 
+func TestReadCanonicalHead(t *testing.T) {
+	db := setupTestDB(t)
+	defer db.Close()
+	tx, err := db.BeginRw(context.Background())
+	require.NoError(t, err)
+	defer tx.Rollback()
+
+	slot, root, err := ReadCanonicalHead(tx)
+	require.NoError(t, err)
+	require.Zero(t, slot)
+	require.Equal(t, common.Hash{}, root)
+
+	root10 := common.Hash{0x10}
+	root12 := common.Hash{0x12}
+	root11 := common.Hash{0x11}
+	require.NoError(t, MarkRootCanonical(context.Background(), tx, 10, root10))
+	require.NoError(t, MarkRootCanonical(context.Background(), tx, 12, root12))
+	require.NoError(t, MarkRootCanonical(context.Background(), tx, 11, root11))
+
+	slot, root, err = ReadCanonicalHead(tx)
+	require.NoError(t, err)
+	require.Equal(t, uint64(12), slot)
+	require.Equal(t, root12, root)
+}
+
 func TestReadBeaconBlockHeader(t *testing.T) {
 	db := setupTestDB(t)
 	defer db.Close()
```

### cl/phase1/stages/forkchoice.go
```diff
@@ -107,16 +107,10 @@ func updateCanonicalChainInTheDatabase(ctx context.Context, tx kv.RwTx, headSlot
 		return fmt.Errorf("failed to read canonical block root: %w", err)
 	}
 
-	oldCanonical := common.Hash{}
-	// Guard against uint64 underflow: currentSlot=0 → currentSlot-1 = MaxUint64 → infinite loop.
-	for i := currentSlot; i > 1; i-- {
-		oldCanonical, err = beacon_indicies.ReadCanonicalBlockRoot(tx, i-1)
-		if err != nil {
-			return fmt.Errorf("failed to read canonical block root: %w", err)
-		}
-		if oldCanonical != (common.Hash{}) {
-			break
-		}
+	// Capture the actual old canonical tip before any mutations.
+	oldHeadSlot, oldHeadRoot, err := beacon_indicies.ReadCanonicalHead(tx)
+	if err != nil {
+		return fmt.Errorf("failed to read canonical head: %w", err)
 	}
 
 	// List of new canonical chain entries
@@ -168,16 +162,13 @@ func updateCanonicalChainInTheDatabase(ctx context.Context, tx kv.RwTx, headSlot
 		return fmt.Errorf("failed to mark root canonical: %w", err)
 	}
 
-	// check reorg
-	parentRoot, err := beacon_indicies.ReadParentBlockRoot(ctx, tx, headRoot)
-	if err != nil {
-		return fmt.Errorf("failed to read parent block root: %w", err)
-	}
-	if parentRoot != oldCanonical {
-		log.Debug("cl reorg", "new_head_slot", headSlot, "fork_slot", currentSlot, "old_canonical", oldCanonical, "new_canonical", headRoot)
-		oldStateRoot, err := beacon_indicies.ReadStateRootByBlockRoot(ctx, tx, oldCanonical)
+	// A reorg occurred if the fork point (currentSlot) is strictly below the
+	// old canonical tip. Normal chain extension lands exactly at oldHeadSlot.
+	if oldHeadRoot != (common.Hash{}) && currentSlot < oldHeadSlot {
+		log.Debug("cl reorg", "new_head_slot", headSlot, "fork_slot", currentSlot, "old_head", oldHeadRoot, "new_canonical", headRoot)
+		oldStateRoot, err := beacon_indicies.ReadStateRootByBlockRoot(ctx, tx, oldHeadRoot)
 		if err != nil {
-			log.Warn("failed to read state root by block root", "err", err, "block_root", oldCanonical)
+			log.Warn("failed to read state root by block root", "err", err, "block_root", oldHeadRoot)
 			return nil
 		}
 		newStateRoot, err := beacon_indicies.ReadStateRootByBlockRoot(ctx, tx, headRoot)
@@ -186,18 +177,22 @@ func updateCanonicalChainInTheDatabase(ctx context.Context, tx kv.RwTx, headSlot
 			return nil
 		}
 		reorgDepth := uint64(0)
-		if headSlot > currentSlot {
-			reorgDepth = headSlot - currentSlot
+		if oldHeadSlot > currentSlot {
+			reorgDepth = oldHeadSlot - currentSlot
+		}
+		executionOptimistic := false
+		if cfg.forkChoice != nil {
+			executionOptimistic = cfg.forkChoice.IsRootOptimistic(headRoot)
 		}
 		reorgEvent := &beaconevents.ChainReorgData{
 			Slot:                headSlot,
 			Depth:               reorgDepth,
-			OldHeadBlock:        oldCanonical,
+			OldHeadBlock:        oldHeadRoot,
 			NewHeadBlock:        headRoot,
 			OldHeadState:        oldStateRoot,
 			NewHeadState:        newStateRoot,
 			Epoch:               headSlot / cfg.beaconCfg.SlotsPerEpoch,
-			ExecutionOptimistic: cfg.forkChoice.IsRootOptimistic(headRoot),
+			ExecutionOptimistic: executionOptimistic,
 		}
 		cfg.emitter.State().SendChainReorg(reorgEvent)
 	}
```

### cl/phase1/stages/forkchoice_test.go
```diff
@@ -0,0 +1,258 @@
+package stages
+
+import (
+	"context"
+	"testing"
+
+	"github.com/stretchr/testify/require"
+
+	"github.com/erigontech/erigon/cl/beacon/beaconevents"
+	"github.com/erigontech/erigon/cl/clparams"
+	"github.com/erigontech/erigon/cl/persistence/beacon_indicies"
+	"github.com/erigontech/erigon/common"
+	"github.com/erigontech/erigon/db/kv"
+	"github.com/erigontech/erigon/db/kv/dbcfg"
+	"github.com/erigontech/erigon/db/kv/memdb"
+)
+
+func TestUpdateCanonicalChainReorgEvent(t *testing.T) {
+	db := memdb.NewTestDB(t, dbcfg.ChainDB)
+	defer db.Close()
+
+	ctx := context.Background()
+	tx, err := db.BeginRw(ctx)
+	require.NoError(t, err)
+	defer tx.Rollback()
+
+	root100 := common.Hash{0x10}
+	root101a := common.Hash{0x11, 0xaa}
+	root102a := common.Hash{0x12, 0xaa}
+	root101b := common.Hash{0x11, 0xbb}
+	root102b := common.Hash{0x12, 0xbb}
+
+	state100 := common.Hash{0xa0}
+	state101a := common.Hash{0xa1}
+	state102a := common.Hash{0xa2}
+	state101b := common.Hash{0xb1}
+	state102b := common.Hash{0xb2}
+
+	writeBlock := func(root, parentRoot, stateRoot common.Hash, slot uint64, canonical bool) {
+		t.Helper()
+		require.NoError(t, beacon_indicies.WriteHeaderSlot(tx, root, slot))
+		require.NoError(t, beacon_indicies.WriteParentBlockRoot(ctx, tx, root, parentRoot))
+		require.NoError(t, beacon_indicies.WriteStateRoot(tx, root, stateRoot))
+		if canonical {
+			require.NoError(t, beacon_indicies.MarkRootCanonical(ctx, tx, slot, root))
+		}
+	}
+
+	writeBlock(root100, common.Hash{0x99}, state100, 100, true)
+	writeBlock(root101a, root100, state101a, 101, true)
+	writeBlock(root102a, root101a, state102a, 102, true)
+
+	writeBlock(root101b, root100, state101b, 101, false)
+	writeBlock(root102b, root101b, state102b, 102, false)
+
+	reorg := drainReorgEvent(t, ctx, tx, 102, root102b)
+	require.NotNil(t, reorg, "expected a chain_reorg event to be emitted")
+	require.Equal(t, uint64(102), reorg.Slot, "reorg Slot")
+	require.Equal(t, uint64(2), reorg.Depth, "reorg Depth should be oldHeadSlot - forkPointSlot")
+	require.Equal(t, root102a, reorg.OldHeadBlock, "OldHeadBlock should be the previous canonical tip")
+	require.Equal(t, root102b, reorg.NewHeadBlock, "NewHeadBlock")
+	require.Equal(t, state102a, reorg.OldHeadState, "OldHeadState should match old canonical tip's state root")
+	require.Equal(t, state102b, reorg.NewHeadState, "NewHeadState")
+}
+
+func TestUpdateCanonicalChainReorgShorterFork(t *testing.T) {
+	db := memdb.NewTestDB(t, dbcfg.ChainDB)
+	defer db.Close()
+
+	ctx := context.Background()
+	tx, err := db.BeginRw(ctx)
+	require.NoError(t, err)
+	defer tx.Rollback()
+
+	root100 := common.Hash{0x10}
+	root101a := common.Hash{0x11, 0xaa}
+	root102a := common.Hash{0x12, 0xaa}
+	root103a := common.Hash{0x13, 0xaa}
+	root101b := common.Hash{0x11, 0xbb}
+	root102b := common.Hash{0x12, 0xbb}
+
+	state100 := common.Hash{0xa0}
+	state103a := common.Hash{0xa3}
+	state102b := common.Hash{0xb2}
+
+	writeBlock := func(root, parentRoot, stateRoot common.Hash, slot uint64, canonical bool) {
+		t.Helper()
+		require.NoError(t, beacon_indicies.WriteHeaderSlot(tx, root, slot))
+		require.NoError(t, beacon_indicies.WriteParentBlockRoot(ctx, tx, root, parentRoot))
+		require.NoError(t, beacon_indicies.WriteStateRoot(tx, root, stateRoot))
+		if canonical {
+			require.NoError(t, beacon_indicies.MarkRootCanonical(ctx, tx, slot, root))
+		}
+	}
+
+	writeBlock(root100, common.Hash{0x99}, state100, 100, true)
+	writeBlock(root101a, root100, common.Hash{0xa1}, 101, true)
+	writeBlock(root102a, root101a, common.Hash{0xa2}, 102, true)
+	writeBlock(root103a, root102a, state103a, 103, true)
+
+	writeBlock(root101b, root100, common.Hash{0xb1}, 101, false)
+	writeBlock(root102b, root101b, state102b, 102, false)
+
+	reorg := drainReorgEvent(t, ctx, tx, 102, root102b)
+	require.NotNil(t, reorg, "expected a chain_reorg event to be emitted")
+	require.Equal(t, uint64(102), reorg.Slot, "reorg Slot")
+	require.Equal(t, uint64(3), reorg.Depth, "reorg Depth: old tip 103 - fork point 100 = 3")
+	require.Equal(t, root103a, reorg.OldHeadBlock, "OldHeadBlock must be the actual old tip at slot 103, not 102a")
+	require.Equal(t, root102b, reorg.NewHeadBlock, "NewHeadBlock")
+	require.Equal(t, state103a, reorg.OldHeadState, "OldHeadState must match old tip's state root")
+	require.Equal(t, state102b, reorg.NewHeadState, "NewHeadState")
+}
+
+func TestUpdateCanonicalChainReorgLongerFork(t *testing.T) {
+	db := memdb.NewTestDB(t, dbcfg.ChainDB)
+	defer db.Close()
+
+	ctx := context.Background()
+	tx, err := db.BeginRw(ctx)
+	require.NoError(t, err)
+	defer tx.Rollback()
+
+	root100 := common.Hash{0x10}
+	root101a := common.Hash{0x11, 0xaa}
+	root102a := common.Hash{0x12, 0xaa}
+	root101b := common.Hash{0x11, 0xbb}
+	root102b := common.Hash{0x12, 0xbb}
+	root103b := common.Hash{0x13, 0xbb}
+
+	state102a := common.Hash{0xa2}
+	state103b := common.Hash{0xb3}
+
+	writeBlock := func(root, parentRoot, stateRoot common.Hash, slot uint64, canonical bool) {
+		t.Helper()
+		require.NoError(t, beacon_indicies.WriteHeaderSlot(tx, root, slot))
+		require.NoError(t, beacon_indicies.WriteParentBlockRoot(ctx, tx, root, parentRoot))
+		require.NoError(t, beacon_indicies.WriteStateRoot(tx, root, stateRoot))
+		if canonical {
+			require.NoError(t, beacon_indicies.MarkRootCanonical(ctx, tx, slot, root))
+		}
+	}
+
+	writeBlock(root100, common.Hash{0x99}, common.Hash{0xa0}, 100, true)
+	writeBlock(root101a, root100, common.Hash{0xa1}, 101, true)
+	writeBlock(root102a, root101a, state102a, 102, true)
+
+	writeBlock(root101b, root100, common.Hash{0xb1}, 101, false)
+	writeBlock(root102b, root101b, common.Hash{0xb2}, 102, false)
+	writeBlock(root103b, root102b, state103b, 103, false)
+
+	reorg := drainReorgEvent(t, ctx, tx, 103, root103b)
+	require.NotNil(t, reorg, "expected a chain_reorg event to be emitted")
+	require.Equal(t, uint64(103), reorg.Slot, "reorg Slot")
+	require.Equal(t, uint64(2), reorg.Depth, "reorg Depth: old tip 102 - fork point 100 = 2")
+	require.Equal(t, root102a, reorg.OldHeadBlock, "OldHeadBlock must be the old tip at slot 102")
+	require.Equal(t, root103b, reorg.NewHeadBlock, "NewHeadBlock")
+	require.Equal(t, state102a, reorg.OldHeadState, "OldHeadState")
+	require.Equal(t, state103b, reorg.NewHeadState, "NewHeadState")
+}
+
+func TestUpdateCanonicalChainNoReorg(t *testing.T) {
+	db := memdb.NewTestDB(t, dbcfg.ChainDB)
+	defer db.Close()
+
+	ctx := context.Background()
+	tx, err := db.BeginRw(ctx)
+	require.NoError(t, err)
+	defer tx.Rollback()
+
+	root100 := common.Hash{0x10}
+	root101 := common.Hash{0x11}
+	root102 := common.Hash{0x12}
+
+	writeBlock := func(root, parentRoot, stateRoot common.Hash, slot uint64, canonical bool) {
+		t.Helper()
+		require.NoError(t, beacon_indicies.WriteHeaderSlot(tx, root, slot))
+		require.NoError(t, beacon_indicies.WriteParentBlockRoot(ctx, tx, root, parentRoot))
+		require.NoError(t, beacon_indicies.WriteStateRoot(tx, root, stateRoot))
+		if canonical {
+			require.NoError(t, beacon_indicies.MarkRootCanonical(ctx, tx, slot, root))
+		}
+	}
+
+	writeBlock(root100, common.Hash{0x99}, common.Hash{0xa0}, 100, true)
+	writeBlock(root101, root100, common.Hash{0xa1}, 101, true)
+
+	writeBlock(root102, root101, common.Hash{0xa2}, 102, false)
+
+	reorg := drainReorgEvent(t, ctx, tx, 102, root102)
+	require.Nil(t, reorg, "chain extension should NOT emit a chain_reorg event")
+}
+
+func TestUpdateCanonicalChainReorgOneSlot(t *testing.T) {
+	db := memdb.NewTestDB(t, dbcfg.ChainDB)
+	defer db.Close()
+
+	ctx := context.Background()
+	tx, err := db.BeginRw(ctx)
+	require.NoError(t, err)
+	defer tx.Rollback()
+
+	root100 := common.Hash{0x10}
+	root101a := common.Hash{0x11, 0xaa}
+	root101b := common.Hash{0x11, 0xbb}
+
+	state101a := common.Hash{0xa1}
+	state101b := common.Hash{0xb1}
+
+	writeBlock := func(root, parentRoot, stateRoot common.Hash, slot uint64, canonical bool) {
+		t.Helper()
+		require.NoError(t, beacon_indicies.WriteHeaderSlot(tx, root, slot))
+		require.NoError(t, beacon_indicies.WriteParentBlockRoot(ctx, tx, root, parentRoot))
+		require.NoError(t, beacon_indicies.WriteStateRoot(tx, root, stateRoot))
+		if canonical {
+			require.NoError(t, beacon_indicies.MarkRootCanonical(ctx, tx, slot, root))
+		}
+	}
+
+	writeBlock(root100, common.Hash{0x99}, common.Hash{0xa0}, 100, true)
+	writeBlock(root101a, root100, state101a, 101, true)
+	writeBlock(root101b, root100, state101b, 101, false)
+
+	reorg := drainReorgEvent(t, ctx, tx, 101, root101b)
+	require.NotNil(t, reorg, "expected a chain_reorg event to be emitted")
+	require.Equal(t, uint64(101), reorg.Slot, "reorg Slot")
+	require.Equal(t, uint64(1), reorg.Depth, "reorg Depth: old tip 101 - fork point 100 = 1")
+	require.Equal(t, root101a, reorg.OldHeadBlock, "OldHeadBlock must be root_101a")
+	require.Equal(t, root101b, reorg.NewHeadBlock, "NewHeadBlock")
+	require.Equal(t, state101a, reorg.OldHeadState, "OldHeadState")
+	require.Equal(t, state101b, reorg.NewHeadState, "NewHeadState")
+}
+
+func drainReorgEvent(t *testing.T, ctx context.Context, tx kv.RwTx, headSlot uint64, headRoot common.Hash) *beaconevents.ChainReorgData {
+	t.Helper()
+	emitter := beaconevents.NewEventEmitter()
+	ch := make(chan *beaconevents.EventStream, 16)
+	sub := emitter.State().Subscribe(ch)
+	defer sub.Unsubscribe()
+
+	cfg := &Cfg{
+		emitter:   emitter,
+		beaconCfg: &clparams.MainnetBeaconConfig,
+	}
+
+	err := updateCanonicalChainInTheDatabase(ctx, tx, headSlot, headRoot, cfg)
+	require.NoError(t, err)
+
+	for {
+		select {
+		case evt := <-ch:
+			if evt.Event == beaconevents.StateChainReorg {
+				return evt.Data.(*beaconevents.ChainReorgData)
+			}
+		default:
+			return nil
+		}
+	}
+}
```
