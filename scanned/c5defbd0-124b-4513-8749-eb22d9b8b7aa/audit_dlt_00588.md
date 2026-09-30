# [?] forkchoice: fix forkchoice balance underflow when att slot change (#16520)

## Summary
Severity: Unknown
Chain: Ethereum
Component: prysmaticlabs/prysm
Published: 2026-03-13
Source: https://github.com/OffchainLabs/prysm/commit/6605dfbd502422c61154f2e21655ae8f8621b109
Type: security-commit

## Details
forkchoice: fix forkchoice balance underflow when att slot change (#16520)

In ePBS, `resolveVoteNode` routes validator balances to two different
accumulators based on the attestation slot:

When a validator re-attests for the **same block** in a **new epoch**
(assigned to a different slot), the root and payload status are
unchanged. The trigger condition:

  ```go
if vote.currentRoot != vote.nextRoot || oldBalance != newBalance ||
vote.currentPayloadStatus != vote.nextPayloadStatus {
```
  ...does not fire, so the balance is never moved. But the vote rotation silently updates currentSlot to the new value. On the next vote change, the subtraction targets the wrong accumulator (which has balance=0), causing the underflow.

  Examples:
  1. Epoch 2: Validator attests at slot 95 for block B (slot 95).
  pending = (95 == 95) = true → 32 ETH added to `Node.balance`
  2. Epoch 3: Validator re-attests at slot 96 for same block `B.Root/payloadStatus` went from pending to empty → not reprocessed. And currentSlot rotated to 96.
  3. Epoch 4: Validator attests for block C. Subtract from B that's no longer pending but has zero balance which triggers underflow

## Patch
### beacon-chain/forkchoice/doubly-linked-tree/ffg_update_test.go
```diff
@@ -161,7 +161,7 @@ func TestFFGUpdates_TwoBranches(t *testing.T) {
 	//               7   8
 	//               |   |
 	//               9  10
-	f.ProcessAttestation(t.Context(), []uint64{0}, indexToHash(1), 0, true)
+	f.ProcessAttestation(t.Context(), []uint64{0}, indexToHash(1), 1, true)
 
 	// With the additional vote to the left branch, the head should be 9:
 	//           0  <-- start
@@ -191,7 +191,7 @@ func TestFFGUpdates_TwoBranches(t *testing.T) {
 	//               7   8
 	//               |   |
 	//               9  10
-	f.ProcessAttestation(t.Context(), []uint64{1}, indexToHash(2), 0, true)
+	f.ProcessAttestation(t.Context(), []uint64{1}, indexToHash(2), 1, true)
 
 	// With the additional vote to the right branch, the head should be 10:
 	//           0  <-- start
```

### beacon-chain/forkchoice/doubly-linked-tree/forkchoice.go
```diff
@@ -309,8 +309,8 @@ func (f *ForkChoice) updateBalances() error {
 			newBalance = newBalances[index]
 		}
 
-		// Update only if the validator's balance or vote has changed.
-		if vote.currentRoot != vote.nextRoot || oldBalance != newBalance || vote.currentPayloadStatus != vote.nextPayloadStatus {
+		// Update only if the validator's voting slot has changed.
+		if vote.currentSlot != vote.nextSlot {
 			// Add new balance to the next vote target if the root is known.
 			pn, pending := f.store.resolveVoteNode(vote.nextRoot, vote.nextSlot, vote.nextPayloadStatus)
 			if pn != nil && vote.nextRoot != zHash {
```

### beacon-chain/forkchoice/doubly-linked-tree/forkchoice_test.go
```diff
@@ -93,9 +93,9 @@ func TestForkChoice_UpdateBalancesPositiveChange(t *testing.T) {
 	require.NoError(t, f.InsertNode(ctx, st, roblock))
 
 	f.votes = []Vote{
-		{indexToHash(1), indexToHash(1), 0, 0, true, true},
-		{indexToHash(2), indexToHash(2), 0, 0, true, true},
-		{indexToHash(3), indexToHash(3), 0, 0, true, true},
+		{indexToHash(1), indexToHash(1), 1, 0, true, true},
+		{indexToHash(2), indexToHash(2), 2, 0, true, true},
+		{indexToHash(3), indexToHash(3), 3, 0, true, true},
 	}
 
 	// Each node gets one unique vote. The weight should look like 103 <- 102 <- 101 because
@@ -127,9 +127,9 @@ func TestForkChoice_UpdateBalancesNegativeChange(t *testing.T) {
 
 	f.balances = []uint64{100, 100, 100}
 	f.votes = []Vote{
-		{indexToHash(1), indexToHash(1), 0, 0, true, true},
-		{indexToHash(2), indexToHash(2), 0, 0, true, true},
-		{indexToHash(3), indexToHash(3), 0, 0, true, true},
+		{indexToHash(1), indexToHash(1), 1, 0, true, true},
+		{indexToHash(2), indexToHash(2), 2, 0, true, true},
+		{indexToHash(3), indexToHash(3), 3, 0, true, true},
 	}
 
 	f.justifiedBalances = []uint64{10, 20, 30}
@@ -158,9 +158,9 @@ func TestForkChoice_UpdateBalancesUnderflow(t *testing.T) {
 
 	f.balances = []uint64{125, 125, 125}
 	f.votes = []Vote{
-		{indexToHash(1), indexToHash(1), 0, 0, true, true},
-		{indexToHash(2), indexToHash(2), 0, 0, true, true},
-		{indexToHash(3), indexToHash(3), 0, 0, true, true},
+		{indexToHash(1), indexToHash(1), 1, 0, true, true},
+		{indexToHash(2), indexToHash(2), 2, 0, true, true},
+		{indexToHash(3), indexToHash(3), 3, 0, true, true},
 	}
 
 	f.justifiedBalances = []uint64{10, 20, 30}
```

### beacon-chain/forkchoice/doubly-linked-tree/gloas_test.go
```diff
@@ -1486,3 +1486,73 @@ func TestFullHead_PreGloasBlock_ReturnsFalse(t *testing.T) {
 	assert.Equal(t, rootA, hr)
 	assert.Equal(t, false, full, "pre-Gloas block must return full=false from FullHead")
 }
+
+func TestUpdateBalances_SlotChangeMovesBalance(t *testing.T) {
+	f := setupGloas(t, 1, 1)
+	ctx := t.Context()
+	zeroHash := params.BeaconConfig().ZeroHash
+
+	// Insert block B at slot 100 and block C at slot 101.
+	slotB := primitives.Slot(100)
+	rootB := indexToHash(1)
+	blockHashB := indexToHash(100)
+	driftGenesisTime(f, slotB, 0)
+	st, blk, err := prepareGloasForkchoiceState(ctx, slotB, rootB, zeroHash, blockHashB, zeroHash, 1, 1)
+	require.NoError(t, err)
+	require.NoError(t, f.InsertNode(ctx, st, blk))
+
+	slotC := primitives.Slot(101)
+	rootC := indexToHash(2)
+	blockHashC := indexToHash(200)
+	driftGenesisTime(f, slotC, 0)
+	// Use zeroHash as parentBlockHash so C builds on B's empty node (no full node needed).
+	st, blk, err = prepareGloasForkchoiceState(ctx, slotC, rootC, rootB, blockHashC, zeroHash, 1, 1)
+	require.NoError(t, err)
+	require.NoError(t, f.InsertNode(ctx, st, blk))
+
+	s := f.store
+	validatorBalance := uint64(32000000000)
+	f.justifiedBalances = []uint64{validatorBalance}
+
+	// Step 1: Validator attests for block B at slot 100 (same slot as block) with payloadStatus=false.
+	// resolveVoteNode(B, 100, false) → pending = (100 == 100) = true → Node.balance.
+	f.votes = []Vote{
+		{currentRoot: zeroHash, nextRoot: rootB, nextSlot: slotB, currentSlot: 0, nextPayloadStatus: false, currentPayloadStatus: false},
+	}
+	require.NoError(t, f.updateBalances())
+
+	emptyB := s.emptyNodeByRoot[rootB]
+	require.NotNil(t, emptyB)
+	assert.Equal(t, validatorBalance, emptyB.node.balance, "balance should be in Node.balance (pending)")
+	assert.Equal(t, uint64(0), emptyB.balance, "PayloadNode.balance should be zero")
+
+	// Step 2: Validator re-attests for the same block B but at slot 140 (new epoch, different slot).
+	// payloadStatus and root are unchanged, only the slot changes.
+	laterSlot := primitives.Slot(140)
+	f.votes[0].nextSlot = laterSlot
+	// nextRoot is still B, nextPayloadStatus is still false.
+
+	// Step 3: updateBalances should detect the slot change and reprocess.
+	// It should subtract from Node.balance (pending, old slot 100==100) and
+	// add to PayloadNode.balance (non-pending, new slot 140!=100).
+	require.NoError(t, f.updateBalances())
+
+	assert.Equal(t, uint64(0), emptyB.node.balance, "Node.balance should be zero after slot change moved balance out")
+	assert.Equal(t, validatorBalance, emptyB.balance, "balance should have moved to PayloadNode.balance (non-pending)")
+
+	// Step 4: Validator switches vote to block C at slot 101.
+	// The subtract from B should now correctly target PayloadNode.balance (non-pending).
+	f.votes[0].nextRoot = rootC
+	f.votes[0].nextSlot = slotC
+	require.NoError(t, f.updateBalances())
+
+	// B's balances should both be zero (balance was correctly subtracted).
+	assert.Equal(t, uint64(0), emptyB.node.balance, "Node.balance should remain zero")
+	assert.Equal(t, uint64(0), emptyB.balance, "PayloadNode.balance should be zero after vote moved to C")
+
+	// C should have received the balance.
+	emptyC := s.emptyNodeByRoot[rootC]
+	require.NotNil(t, emptyC)
+	// slot 101 == C.node.slot(101) → pending=true → Node.balance
+	assert.Equal(t, validatorBalance, emptyC.node.balance, "C should have the validator's balance")
+}
```

### beacon-chain/forkchoice/doubly-linked-tree/proposer_boost_test.go
```diff
@@ -63,7 +63,7 @@ func TestForkChoice_BoostProposerRoot_PreventsExAnteAttack(t *testing.T) {
 		)
 		require.NoError(t, err)
 		require.NoError(t, f.InsertNode(ctx, state, blkRoot))
-		f.ProcessAttestation(ctx, []uint64{0}, newRoot, primitives.Slot(fEpoch), true)
+		f.ProcessAttestation(ctx, []uint64{0}, newRoot, slot, true)
 		headRoot, err = f.Head(ctx)
 		require.NoError(t, err)
 		assert.Equal(t, newRoot, headRoot, "Incorrect head for justified epoch at slot 1")
@@ -89,7 +89,7 @@ func TestForkChoice_BoostProposerRoot_PreventsExAnteAttack(t *testing.T) {
 		)
 		require.NoError(t, err)
 		require.NoError(t, f.InsertNode(ctx, state, blkRoot))
-		f.ProcessAttestation(ctx, []uint64{1}, newRoot, primitives.Slot(fEpoch), true)
+		f.ProcessAttestation(ctx, []uint64{1}, newRoot, slot, true)
 		headRoot, err = f.Head(ctx)
 		require.NoError(t, err)
 		assert.Equal(t, newRoot, headRoot, "Incorrect head for justified epoch at slot 2")
@@ -117,7 +117,7 @@ func TestForkChoice_BoostProposerRoot_PreventsExAnteAttack(t *testing.T) {
 		)
 		require.NoError(t, err)
 		require.NoError(t, f.InsertNode(ctx, state, blkRoot))
-		f.ProcessAttestation(ctx, []uint64{2}, newRoot, primitives.Slot(fEpoch), true)
+		f.ProcessAttestation(ctx, []uint64{2}, newRoot, slot, true)
 		headRoot, err = f.Head(ctx)
 		require.NoError(t, err)
 		assert.Equal(t, newRoot, headRoot, "Incorrect head for justified epoch at slot 3")
@@ -146,7 +146,7 @@ func TestForkChoice_BoostProposerRoot_PreventsExAnteAttack(t *testing.T) {
 		)
 		require.NoError(t, err)
 		require.NoError(t, f.InsertNode(ctx, state, blkRoot))
-		f.ProcessAttestation(ctx, []uint64{3}, newRoot, primitives.Slot(fEpoch), true)
+		f.ProcessAttestation(ctx, []uint64{3}, newRoot, slot, true)
 		headRoot, err = f.Head(ctx)
 		require.NoError(t, err)
 		assert.Equal(t, newRoot, headRoot, "Incorrect head for justified epoch at slot 3")
@@ -176,7 +176,7 @@ func TestForkChoice_BoostProposerRoot_PreventsExAnteAttack(t *testing.T) {
 
 		// Regression: process attestations for C, check that it
 		// becomes head, we need two attestations to have C.weight = 30 > 24 = D.weight
-		f.ProcessAttestation(ctx, []uint64{4, 5}, indexToHash(3), primitives.Slot(fEpoch), true)
+		f.ProcessAttestation(ctx, []uint64{4, 5}, indexToHash(3), slot+1, true)
 		headRoot, err = f.Head(ctx)
 		require.NoError(t, err)
 		assert.Equal(t, indexToHash(3), headRoot, "Incorrect head for justified epoch at slot 4")
@@ -237,10 +237,10 @@ func TestForkChoice_BoostProposerRoot_PreventsExAnteAttack(t *testing.T) {
 
 		// The maliciously withheld block has one vote.
 		votes := []uint64{1}
-		f.ProcessAttestation(ctx, votes, maliciouslyWithheldBlock, primitives.Slot(fEpoch), true)
+		f.ProcessAttestation(ctx, votes, maliciouslyWithheldBlock, maliciouslyWithheldBlockSlot, true)
 		// The honest block has one vote.
 		votes = []uint64{2}
-		f.ProcessAttestation(ctx, votes, honestBlock, primitives.Slot(fEpoch), true)
+		f.ProcessAttestation(ctx, votes, honestBlock, honestBlockSlot, true)
 
 		// Ensure the head is STILL C, the honest block, as the honest block had proposer boost.
 		r, err = f.Head(ctx)
@@ -306,7 +306,7 @@ func TestForkChoice_BoostProposerRoot_PreventsExAnteAttack(t *testing.T) {
 		// An attestation is received for B that has more voting power than C with the proposer boost,
 		// allowing B to then become the head if their attestation has enough adversarial votes.
 		votes := []uint64{1, 2}
-		f.ProcessAttestation(ctx, votes, maliciouslyWithheldBlock, primitives.Slot(fEpoch), true)
+		f.ProcessAttestation(ctx, votes, maliciouslyWithheldBlock, maliciouslyWithheldBlockSlot, true)
 
 		// Expect the head to have switched to B.
 		r, err = f.Head(ctx)
@@ -381,7 +381,7 @@ func TestForkChoice_BoostProposerRoot_PreventsExAnteAttack(t *testing.T) {
 
 		// An attestation for C is received at slot N+3.
 		votes := []uint64{1}
-		f.ProcessAttestation(ctx, votes, c, primitives.Slot(fEpoch), true)
+		f.ProcessAttestation(ctx, votes, c, cSlot, true)
 
 		// A block D, building on B, is received at slot N+3. It should not be able to win without boosting.
 		dSlot := primitives.Slot(3)
@@ -421,7 +421,7 @@ func TestForkChoice_BoostProposerRoot_PreventsExAnteAttack(t *testing.T) {
 		require.NoError(t, f.InsertNode(ctx, state, blkRoot))
 
 		votes = []uint64{2}
-		f.ProcessAttestation(ctx, votes, d2, primitives.Slot(fEpoch), true)
+		f.ProcessAttestation(ctx, votes, d2, dSlot, true)
 		// Ensure D becomes the head thanks to boosting.
 		r, err = f.Head(ctx)
 		require.NoError(t, err)
```

### beacon-chain/forkchoice/doubly-linked-tree/reorg_late_blocks_test.go
```diff
@@ -26,7 +26,7 @@ func TestForkChoice_ShouldOverrideFCU(t *testing.T) {
 	for i := range attesters {
 		attesters[i] = uint64(i + 64)
 	}
-	f.ProcessAttestation(ctx, attesters, blk.Root(), 0, true)
+	f.ProcessAttestation(ctx, attesters, blk.Root(), 1, true)
 
 	orphanLateBlockFirstThreshold := time.Duration(params.BeaconConfig().SecondsPerSlot/params.BeaconConfig().IntervalsPerSlot) * time.Second
 	driftGenesisTime(f, 2, orphanLateBlockFirstThreshold+time.Second)
@@ -124,7 +124,7 @@ func TestForkChoice_GetProposerHead(t *testing.T) {
 	for i := range attesters {
 		attesters[i] = uint64(i + 64)
 	}
-	f.ProcessAttestation(ctx, attesters, blk.Root(), 0, true)
+	f.ProcessAttestation(ctx, attesters, blk.Root(), 1, true)
 
 	driftGenesisTime(f, 3, 1*time.Second)
 	childRoot := [32]byte{'b'}
```

### beacon-chain/forkchoice/doubly-linked-tree/vote_test.go
```diff
@@ -243,20 +243,23 @@ func TestVotes_CanFindHead(t *testing.T) {
 
 	// Set the f.justifiedBalances of the last 2 validators to 0.
 	f.justifiedBalances = []uint64{1, 1, 1, 0, 0}
+	f.ProcessAttestation(t.Context(), []uint64{3, 4}, indexToHash(9), 6*params.BeaconConfig().SlotsPerEpoch, true)
 	// The head should be back to 10.
 	r, err = f.Head(t.Context())
 	require.NoError(t, err)
 	assert.Equal(t, indexToHash(10), r, "Incorrect head for with justified epoch at 3")
 
 	// Set the f.justifiedBalances back to normal.
 	f.justifiedBalances = []uint64{1, 1, 1, 1, 1}
+	f.ProcessAttestation(t.Context(), []uint64{3, 4}, indexToHash(9), 7*params.BeaconConfig().SlotsPerEpoch, true)
 	// The head should be back to 9.
 	r, err = f.Head(t.Context())
 	require.NoError(t, err)
 	assert.Equal(t, indexToHash(9), r, "Incorrect head for with justified epoch at 3")
 
 	// Remove the last 2 validators.
 	f.justifiedBalances = []uint64{1, 1, 1}
+	f.ProcessAttestation(t.Context(), []uint64{3, 4}, indexToHash(9), 8*params.BeaconConfig().SlotsPerEpoch, true)
 	// The head should be back to 10.
 	r, err = f.Head(t.Context())
 	require.NoError(t, err)
```

### changelog/t_fix-forkchoice-balance-slot-change.md
```diff
@@ -0,0 +1,2 @@
+### Fixed
+- Fix forkchoice balance underflow when attestation slot changes across epochs for the same head block.
```
