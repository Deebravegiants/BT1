# [?] Fix Forkchoice panic (#16728)

## Summary
Severity: Unknown
Chain: Ethereum
Component: prysmaticlabs/prysm
Published: 2026-05-19
Source: https://github.com/OffchainLabs/prysm/commit/441cfe0ad6be0d09c57a3485c7696dd622021f92
Type: security-commit

## Details
Fix Forkchoice panic (#16728)

This PR adds a fix for a forkchoice panic whenever there are orphaned
blocks in the end of an epoch. We removed children of empty nodes but
not full nodes.

---------

Co-authored-by: Claude Opus 4.7 <noreply@anthropic.com>
Co-authored-by: terence <terence@prysmaticlabs.com>

## Patch
### beacon-chain/forkchoice/doubly-linked-tree/gloas.go
```diff
@@ -93,6 +93,10 @@ func (s *Store) applyWeightChangesConsensusNode(ctx context.Context, n *Node) er
 // applyWeightChangesPayloadNode recomputes the weight of the node passed as an argument and all of its descendants,
 // using the current balance stored in each node.
 func (s *Store) applyWeightChangesPayloadNode(ctx context.Context, n *PayloadNode) error {
+	if n == nil {
+		log.Error("tried to apply weight changes to a nil payload node")
+		return nil
+	}
 	// Recursively calling the children to sum their weights.
 	childrenWeight := uint64(0)
 	for _, child := range n.children {
```

### beacon-chain/forkchoice/doubly-linked-tree/gloas_test.go
```diff
@@ -1633,3 +1633,48 @@ func TestLatestCanonicalHashForRoot_SameParentReorg(t *testing.T) {
 	require.NotEqual(t, blockHashA, got, "should NOT return A's reorged-out payload hash")
 	require.Equal(t, zeroHash, got, "should return the common EL ancestor hash (genesis)")
 }
+
+// Regression test for the prune fix that removes children of the full
+// finalized node with slot <= checkpointMaxSlot. Without the fix, a child
+// built on the full payload of the finalized block survives in
+// fullNodeByRoot/emptyNodeByRoot and can later trigger a panic.
+func TestStore_Prune_IncompatibleFullFinalizedChildren(t *testing.T) {
+	f := setupGloas(t, 0, 0)
+	ctx := t.Context()
+
+	// Block A at slot 30 (epoch 0), child of genesis.
+	rootA := indexToHash(1)
+	blockHashA := indexToHash(100)
+	st, roblock, err := prepareGloasForkchoiceState(ctx, 30, rootA, params.BeaconConfig().ZeroHash, blockHashA, params.BeaconConfig().ZeroHash, 0, 0)
+	require.NoError(t, err)
+	require.NoError(t, f.InsertNode(ctx, st, roblock))
+
+	// Insert payload for A so fullNodeByRoot[A] exists.
+	pe, err := prepareGloasForkchoicePayload(rootA)
+	require.NoError(t, err)
+	require.NoError(t, f.InsertPayload(pe))
+
+	// Block C at slot 31 builds on full A.
+	rootC := indexToHash(2)
+	blockHashC := indexToHash(101)
+	st, roblock, err = prepareGloasForkchoiceState(ctx, 31, rootC, rootA, blockHashC, blockHashA, 0, 0)
+	require.NoError(t, err)
+	require.NoError(t, f.InsertNode(ctx, st, roblock))
+
+	s := f.store
+	fullA := s.fullNodeByRoot[rootA]
+	require.NotNil(t, fullA)
+	require.Equal(t, 1, len(fullA.children))
+	require.Equal(t, rootC, fullA.children[0].root)
+	require.NotNil(t, s.emptyNodeByRoot[rootC])
+
+	// Finalize A in epoch 1: checkpointMaxSlot = 32, so C (slot 31) is incompatible.
+	s.finalizedCheckpoint.Root = rootA
+	s.finalizedCheckpoint.Epoch = 1
+	require.NoError(t, s.prune(ctx))
+
+	_, emptyOk := s.emptyNodeByRoot[rootC]
+	require.Equal(t, false, emptyOk)
+	_, fullOk := s.fullNodeByRoot[rootC]
+	require.Equal(t, false, fullOk)
+}
```

### beacon-chain/forkchoice/doubly-linked-tree/store.go
```diff
@@ -286,13 +286,32 @@ func (s *Store) prune(ctx context.Context) error {
 		return nil
 	}
 
+	remaining := fen.children[:0]
 	for _, child := range fen.children {
 		if child != nil && child.slot <= checkpointMaxSlot {
 			if err := s.pruneFinalizedNodeByRootMap(ctx, child, fn); err != nil {
 				return errors.Wrap(err, "could not prune incompatible finalized child")
 			}
+			continue
 		}
+		remaining = append(remaining, child)
 	}
+	fen.children = remaining
+	ffn := s.fullNodeByRoot[finalizedRoot]
+	if ffn == nil {
+		return nil
+	}
+	remaining = ffn.children[:0]
+	for _, child := range ffn.children {
+		if child != nil && child.slot <= checkpointMaxSlot {
+			if err := s.pruneFinalizedNodeByRootMap(ctx, child, fn); err != nil {
+				return errors.Wrap(err, "could not prune incompatible finalized child")
+			}
+			continue
+		}
+		remaining = append(remaining, child)
+	}
+	ffn.children = remaining
 	return nil
 }
 
```

### beacon-chain/forkchoice/doubly-linked-tree/store_test.go
```diff
@@ -181,9 +181,9 @@ func TestStore_Prune_MoreThanOnce(t *testing.T) {
 	assert.Equal(t, 90, len(s.emptyNodeByRoot), "Incorrect nodes count")
 
 	// One more time.
-	s.finalizedCheckpoint.Root = indexToHash(20)
+	s.finalizedCheckpoint.Root = indexToHash(10)
 	require.NoError(t, s.prune(t.Context()))
-	assert.Equal(t, 80, len(s.emptyNodeByRoot), "Incorrect nodes count")
+	assert.Equal(t, 90, len(s.emptyNodeByRoot), "Incorrect nodes count")
 }
 
 func TestStore_Prune_ReturnEarly(t *testing.T) {
```

### changelog/potuz_fc_panic.md
```diff
@@ -0,0 +1,2 @@
+### Fixed
+- Prune children of full finalized that are incompatible with it. 
```
