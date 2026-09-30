# [?] consensus: fix milestone-mismatch rewind deadlock (#2246)

## Summary
Severity: Unknown
Chain: Polygon
Component: 0xPolygon/bor
Published: 2026-05-29
Source: https://github.com/0xPolygon/bor/commit/b267c75c357db127e3c58e1e40ec8d42ee31a2d5
Type: security-commit

## Details
consensus: fix milestone-mismatch rewind deadlock (#2246)

## Patch
### core/forkchoice_test.go
```diff
@@ -306,8 +306,9 @@ func (w *chainValidatorFake) GetWhitelistedCheckpoint() (bool, uint64, common.Ha
 func (w *chainValidatorFake) GetWhitelistedMilestone() (bool, uint64, common.Hash) {
 	return false, 0, common.Hash{}
 }
-func (w *chainValidatorFake) PurgeWhitelistedCheckpoint() {}
-func (w *chainValidatorFake) PurgeWhitelistedMilestone()  {}
+func (w *chainValidatorFake) PurgeWhitelistedCheckpoint()   {}
+func (w *chainValidatorFake) PurgeWhitelistedMilestone()    {}
+func (w *chainValidatorFake) PurgeMilestonesAfter(_ uint64) {}
 func (w *chainValidatorFake) GetCheckpoints(current, sidechainHeader *types.Header, sidechainCheckpoints []*types.Header) (map[uint64]*types.Header, error) {
 	return map[uint64]*types.Header{}, nil
 }
```

### core/rawdb/milestone.go
```diff
@@ -118,6 +118,12 @@ func WriteLastFinality[T BlockFinality[T]](db ethdb.KeyValueWriter, block uint64
 	return nil
 }
 
+// DeleteLastFinality removes the persisted whitelist entry for T.
+func DeleteLastFinality[T BlockFinality[T]](db ethdb.KeyValueWriter) error {
+	_, key := getKey[T]()
+	return db.Delete(key)
+}
+
 type BlockFinality[T any] interface {
 	set(block uint64, hash common.Hash)
 	clone() T
@@ -180,7 +186,7 @@ func ReadLockField(db ethdb.KeyValueReader) (bool, uint64, common.Hash, map[stri
 	}
 
 	if err = json.Unmarshal(data, &lockField); err != nil {
-		log.Error(fmt.Sprintf("Unable to unmarshal the lock field in database"), "err", err)
+		log.Error("Unable to unmarshal the lock field in database", "err", err)
 
 		return false, 0, common.Hash{}, nil, fmt.Errorf("%w(%v) for lock field , data %v(%q)",
 			ErrIncorrectLockField, err, data, string(data))
@@ -226,11 +232,11 @@ func ReadFutureMilestoneList(db ethdb.KeyValueReader) ([]uint64, map[uint64]comm
 	}
 
 	if len(data) == 0 {
-		return nil, nil, fmt.Errorf("%w for %s", ErrIncorrectLockField, string(key))
+		return nil, nil, fmt.Errorf("%w for %s", ErrIncorrectFutureMilestoneField, string(key))
 	}
 
 	if err = json.Unmarshal(data, &futureMilestoneField); err != nil {
-		log.Error(fmt.Sprintf("Unable to unmarshal the future milestone field in database"), "err", err)
+		log.Error("Unable to unmarshal the future milestone field in database", "err", err)
 
 		return nil, nil, fmt.Errorf("%w(%v) for future milestone field, data %v(%q)",
 			ErrIncorrectFutureMilestoneField, err, data, string(data))
```

### eth/bor_checkpoint_verifier.go
```diff
@@ -106,35 +106,49 @@ func borVerify(ctx context.Context, eth *Ethereum, handler *ethHandler, start ui
 		ethHandler := (*ethHandler)(eth.handler)
 
 		var (
-			rewindTo uint64
-			doExist  bool
+			rewindTo       uint64
+			rewindToSet    bool
+			rewindAttested bool
 		)
 
-		// First try the original logic to find existing whitelisted milestone/checkpoint
-		if doExist, rewindTo, _ = ethHandler.downloader.GetWhitelistedMilestone(); doExist {
-			// Use existing whitelisted milestone
-			log.Info("Using existing whitelisted milestone for rewind", "block", rewindTo)
-		} else if doExist, rewindTo, _ = ethHandler.downloader.GetWhitelistedCheckpoint(); doExist {
-			// Use existing whitelisted checkpoint
-			log.Info("Using existing whitelisted checkpoint for rewind", "block", rewindTo)
-		} else {
-			// No existing whitelisted milestone/checkpoint found
-			// For milestones, try to find the common ancestor by checking past milestones
-			if !isCheckpoint && end > 0 {
-				log.Info("No existing whitelisted milestone/checkpoint, searching for common ancestor")
-				rewindTo = findCommonAncestorWithFutureMilestones(eth, start, end, hash)
-			} else {
-				// For checkpoints or when start is 0, use simple fallback
-				if start <= 0 {
-					rewindTo = 0
-				} else {
-					rewindTo = start - 1
-				}
+		attestRewindAt := func(num uint64, expectedHash common.Hash) bool {
+			return num < end && eth.BlockChain().GetCanonicalHash(num) == expectedHash
+		}
+
+		// Try anchor sources in attestability order; a non-attesting first source
+		// must not short-circuit later attesting ones.
+		if exists, num, h := ethHandler.downloader.GetWhitelistedMilestone(); exists {
+			rewindTo, rewindToSet = num, true
+			rewindAttested = attestRewindAt(num, h)
+			log.Info("Using existing whitelisted milestone for rewind", "block", rewindTo, "attested", rewindAttested)
+		}
+
+		if !rewindAttested && !isCheckpoint && end > 0 {
+			num, attested := findCommonAncestorWithFutureMilestones(eth, start, end, hash)
+			// Race: findCommonAncestor's re-read of local-at-end may disagree
+			// with the outer mismatch check and yield (end, true).
+			if attested && num < end {
+				rewindTo, rewindToSet, rewindAttested = num, true, true
+				log.Info("Using future-milestone match for rewind", "block", rewindTo)
+			} else if !rewindToSet {
+				rewindTo, rewindToSet = num, true
+			}
+		}
+
+		if !rewindToSet {
+			// Checkpoint hash is a merkle root, never attests; used only for the
+			// refusal-log rewindTo.
+			if exists, num, _ := ethHandler.downloader.GetWhitelistedCheckpoint(); exists {
+				rewindTo = num
+				log.Info("Using existing whitelisted checkpoint for rewind", "block", rewindTo)
+			} else if start > 0 {
+				rewindTo = start - 1
 			}
 		}
 
 		if head-rewindTo > maxRewindLen {
 			rewindTo = head - maxRewindLen
+			rewindAttested = false // clamped target is not the attested block
 		}
 
 		if isCheckpoint {
@@ -166,19 +180,40 @@ func borVerify(ctx context.Context, eth *Ethereum, handler *ethHandler, start ui
 			canonicalChain = nil
 		}
 
-		// Never rewind unless we actually have a canonical chain segment to insert.
-		if len(canonicalChain) == 0 {
-			if isCheckpoint {
-				log.Warn("Checkpoint mismatch: refusing to rewind without a canonical chain segment",
-					"head", head, "rewindTo", rewindTo, "start", start, "end", end)
-			} else {
-				log.Warn("Milestone mismatch: refusing to rewind without a canonical chain segment",
-					"head", head, "rewindTo", rewindTo, "start", start, "end", end)
+		if len(canonicalChain) > 0 {
+			if reorgToFinalized(eth, head, rewindTo, canonicalChain) {
+				ethHandler.downloader.PurgeMilestonesAfter(rewindTo)
+			}
+			return hash, errHashMismatch
+		}
+
+		// No canonical sidechain locally. Recoverable for milestones: SetHead to
+		// an attested ancestor drops the bad-fork tip the downloader rejects as
+		// "sidechain ghost-state attack", letting canonical resync proceed.
+		// maxRewindLen keeps the target inside the in-memory trie window.
+		if !isCheckpoint && rewindAttested && head-rewindTo <= maxRewindLen {
+			log.Warn("Milestone mismatch: rewinding to attested canonical ancestor without local sidechain; canonical chain will resync from peers",
+				"head", head, "rewindTo", rewindTo, "start", start, "end", end)
+
+			defer pauseMiner(eth)()
+			if err := rewind(eth, head, rewindTo); err != nil {
+				// Chain still on bad fork; keep whitelist intact rather than weakening.
+				return hash, errHashMismatch
 			}
+			// Stale future-fork entries would reject canonical peers via
+			// IsValidChain / IsReorgAllowed / IsFutureMilestoneCompatible.
+			ethHandler.downloader.PurgeMilestonesAfter(rewindTo)
 			return hash, errHashMismatch
 		}
-		reorgToFinalized(eth, head, rewindTo, canonicalChain)
 
+		if isCheckpoint {
+			log.Warn("Checkpoint mismatch: refusing to rewind without a canonical chain segment",
+				"head", head, "rewindTo", rewindTo, "start", start, "end", end)
+		} else {
+			log.Warn("Milestone mismatch: refusing to rewind without a canonical chain segment",
+				"head", head, "rewindTo", rewindTo, "start", start, "end", end,
+				"attested", rewindAttested)
+		}
 		return hash, errHashMismatch
 	}
 
@@ -194,47 +229,57 @@ func borVerify(ctx context.Context, eth *Ethereum, handler *ethHandler, start ui
 	return hash, nil
 }
 
-// reorgToFinalized stops the miner if the mining process is running and rewinds back the chain
-// and inserts the chain finalized by checkpoint/milestone.
-func reorgToFinalized(eth *Ethereum, head uint64, rewindTo uint64, canonicalChain []*types.Block) {
-	// do nothing if there is no canonical chain to insert.
+// reorgToFinalized rewinds head to rewindTo and inserts canonicalChain. Returns
+// true if head actually moved (the insert is best-effort and a partial insert
+// still counts).
+func reorgToFinalized(eth *Ethereum, head uint64, rewindTo uint64, canonicalChain []*types.Block) bool {
 	if len(canonicalChain) == 0 {
 		log.Warn("Refusing to reorg finalized without canonical chain",
 			"head", head, "rewindTo", rewindTo)
-		return
+		return false
 	}
 
-	if eth.Miner() != nil && eth.Miner().Mining() {
-		ch := make(chan struct{})
-		eth.Miner().Stop(ch)
-
-		<-ch
+	defer pauseMiner(eth)()
 
-		defer eth.Miner().Start()
+	if err := rewind(eth, head, rewindTo); err != nil {
+		return false
 	}
-
-	rewind(eth, head, rewindTo)
 	insertFinalized(eth, canonicalChain)
+	return true
 }
 
-func rewind(eth *Ethereum, head uint64, rewindTo uint64) {
-	eth.handler.downloader.Cancel()
-	err := eth.blockchain.SetHead(rewindTo)
+// pauseMiner stops the miner and returns a restart function for the caller to
+// defer; the restart fires at the caller's return, not pauseMiner's.
+func pauseMiner(eth *Ethereum) func() {
+	if eth.Miner() == nil || !eth.Miner().Mining() {
+		return func() {}
+	}
+	ch := make(chan struct{})
+	eth.Miner().Stop(ch)
+	<-ch
+	return func() { eth.Miner().Start() }
+}
 
-	if err != nil {
+// rewind cancels in-flight downloads and SetHeads to rewindTo. Callers must
+// check the error before any downstream insert or whitelist purge.
+func rewind(eth *Ethereum, head uint64, rewindTo uint64) error {
+	eth.handler.downloader.Cancel()
+	if err := eth.blockchain.SetHead(rewindTo); err != nil {
 		log.Error("Error while rewinding the chain", "to", rewindTo, "err", err)
-	} else {
-		rewindLengthMeter.Mark(int64(head - rewindTo))
+		return err
 	}
+	rewindLengthMeter.Mark(int64(head - rewindTo))
+	return nil
 }
 
-// findCommonAncestorWithFutureMilestones tries to find where the local chain diverged from the milestone chain
-// by checking blocks backwards from the milestone range
-func findCommonAncestorWithFutureMilestones(eth *Ethereum, start uint64, end uint64, milestoneEndHash string) uint64 {
+// findCommonAncestorWithFutureMilestones returns a candidate rewind anchor.
+// The bool is true only when local hash at the returned block matches a
+// stored milestone hash; callers must not blind-rewind on (_, false).
+func findCommonAncestorWithFutureMilestones(eth *Ethereum, start uint64, end uint64, milestoneEndHash string) (uint64, bool) {
 	// Start from the milestone start block and work backwards
 	// to find where our chain matches the expected chain
 	if start == 0 {
-		return 0
+		return 0, false
 	}
 
 	blockchain := eth.BlockChain()
@@ -245,7 +290,7 @@ func findCommonAncestorWithFutureMilestones(eth *Ethereum, start uint64, end uin
 	if localBlock != nil {
 		localHash := localBlock.Hash().Hex()[2:]
 		if localHash == milestoneEndHash {
-			return end
+			return end, true
 		}
 	}
 
@@ -268,20 +313,16 @@ func findCommonAncestorWithFutureMilestones(eth *Ethereum, start uint64, end uin
 			localBlock := blockchain.GetBlockByNumber(milestoneNum)
 			if localBlock != nil && localBlock.Hash() == milestoneHash {
 				log.Info("Found matching future milestone", "block", milestoneNum, "hash", milestoneHash)
-				return milestoneNum
+				return milestoneNum, true
 			}
 
-			if milestoneNum < targetBlock {
+			if milestoneNum > 0 && milestoneNum < targetBlock {
 				targetBlock = milestoneNum - 1
 			}
 		}
 	}
 
-	if targetBlock < 0 {
-		return 0
-	}
-
-	return targetBlock
+	return targetBlock, false
 }
 
 // insertFinalized inserts the chain finalized by checkpoint/milestone and ensures the final block is set as canonical.
```

### eth/bor_checkpoint_verifier_test.go
```diff
@@ -224,16 +224,11 @@ func findCommonAncestorWithFutureMilestones_CalculateTargetBlock_NoMatch(start u
 			continue // Skip milestones after current one
 		}
 
-		// Update target block based on milestone found (when no hash match)
-		if milestoneNum < targetBlock {
+		if milestoneNum > 0 && milestoneNum < targetBlock {
 			targetBlock = milestoneNum - 1
 		}
 	}
 
-	if targetBlock < 0 {
-		return 0
-	}
-
 	return targetBlock
 }
 
@@ -410,6 +405,200 @@ func TestCheckpointMismatch_DoesNotRewind(t *testing.T) {
 	require.NotNil(t, blockAtEnd, "canonical block at end=%d must remain present", end)
 }
 
+// Whitelist matches local at rewindTo < end: blind rewind fires and purges
+// future entries above the anchor.
+func TestMilestoneMismatch_AttestedRewind_PurgesStaleWhitelist(t *testing.T) {
+	t.Parallel()
+
+	log.SetDefault(log.NewLogger(log.NewTerminalHandlerWithLevel(os.Stderr, log.LevelInfo, true)))
+
+	ctx, cancel := context.WithTimeout(context.Background(), 60*time.Second)
+	defer cancel()
+
+	stack, ethBackend, headBefore := startMinedBorNode(t, 20)
+	defer stack.Close()
+	require.GreaterOrEqual(t, headBefore, uint64(20))
+
+	anchor := headBefore - 10
+	anchorHash := ethBackend.BlockChain().GetBlockByNumber(anchor).Hash()
+
+	dl := ethBackend.handler.downloader
+	dl.ProcessMilestone(anchor, anchorHash)
+
+	staleFutureBlock := headBefore - 5
+	staleLocalHash := ethBackend.BlockChain().GetBlockByNumber(staleFutureBlock).Hash()
+	staleFutureHash := common.HexToHash(mutateHexString(staleLocalHash.Hex()[2:]))
+	require.NotEqual(t, staleLocalHash, staleFutureHash)
+	dl.ProcessFutureMilestone(staleFutureBlock, staleFutureHash)
+
+	doExist, wlNum, wlHash := dl.GetWhitelistedMilestone()
+	require.True(t, doExist)
+	require.Equal(t, anchor, wlNum)
+	require.Equal(t, anchorHash, wlHash)
+	preFutureOrder, preFutureList, err := rawdb.ReadFutureMilestoneList(ethBackend.ChainDb())
+	require.NoError(t, err)
+	require.Contains(t, preFutureOrder, staleFutureBlock)
+	require.Equal(t, staleFutureHash, preFutureList[staleFutureBlock])
+
+	mismatchEnd := headBefore - 3
+	mismatchStart := mismatchEnd - 1
+	mismatchLocal := ethBackend.BlockChain().GetBlockByNumber(mismatchEnd).Hash().Hex()[2:]
+	bogusHash := mutateHexString(mismatchLocal)
+
+	verifier := newBorVerifier()
+	ethHandler := (*ethHandler)(ethBackend.handler)
+
+	_, err = verifier.verify(ctx, ethBackend, ethHandler, mismatchStart, mismatchEnd, bogusHash, false)
+	require.ErrorIs(t, err, errHashMismatch)
+
+	headAfter := ethBackend.BlockChain().CurrentBlock().Number.Uint64()
+	require.Equal(t, anchor, headAfter)
+	require.Equal(t, anchorHash, ethBackend.BlockChain().CurrentBlock().Hash())
+
+	postFutureOrder, postFutureList, _ := rawdb.ReadFutureMilestoneList(ethBackend.ChainDb())
+	require.NotContains(t, postFutureOrder, staleFutureBlock)
+	_, present := postFutureList[staleFutureBlock]
+	require.False(t, present)
+
+	doExist, wlNum, wlHash = dl.GetWhitelistedMilestone()
+	require.True(t, doExist)
+	require.Equal(t, anchor, wlNum)
+	require.Equal(t, anchorHash, wlHash)
+}
+
+// Whitelist hash differs from local at the anchor: blind rewind must refuse.
+func TestMilestoneMismatch_WhitelistHashDiffersFromLocal_DoesNotRewind(t *testing.T) {
+	t.Parallel()
+
+	log.SetDefault(log.NewLogger(log.NewTerminalHandlerWithLevel(os.Stderr, log.LevelInfo, true)))
+
+	ctx, cancel := context.WithTimeout(context.Background(), 60*time.Second)
+	defer cancel()
+
+	stack, ethBackend, headBefore := startMinedBorNode(t, 20)
+	defer stack.Close()
+
+	anchor := headBefore - 10
+	localAtAnchor := ethBackend.BlockChain().GetBlockByNumber(anchor).Hash()
+	whitelistHash := common.HexToHash(mutateHexString(localAtAnchor.Hex()[2:]))
+	require.NotEqual(t, localAtAnchor, whitelistHash)
+
+	ethBackend.handler.downloader.ProcessMilestone(anchor, whitelistHash)
+
+	mismatchEnd := headBefore - 3
+	mismatchStart := mismatchEnd - 1
+	bogusHash := mutateHexString(ethBackend.BlockChain().GetBlockByNumber(mismatchEnd).Hash().Hex()[2:])
+
+	verifier := newBorVerifier()
+	ethHandler := (*ethHandler)(ethBackend.handler)
+
+	_, err := verifier.verify(ctx, ethBackend, ethHandler, mismatchStart, mismatchEnd, bogusHash, false)
+	require.ErrorIs(t, err, errHashMismatch)
+
+	require.Equal(t, headBefore, ethBackend.BlockChain().CurrentBlock().Number.Uint64())
+}
+
+// rewindTo == end (SetHead would no-op for the bad block): blind rewind must refuse.
+func TestMilestoneMismatch_WhitelistAtMismatchHeight_DoesNotRewind(t *testing.T) {
+	t.Parallel()
+
+	log.SetDefault(log.NewLogger(log.NewTerminalHandlerWithLevel(os.Stderr, log.LevelInfo, true)))
+
+	ctx, cancel := context.WithTimeout(context.Background(), 60*time.Second)
+	defer cancel()
+
+	stack, ethBackend, headBefore := startMinedBorNode(t, 20)
+	defer stack.Close()
+
+	sameHeight := headBefore - 5
+	anchorLocal := ethBackend.BlockChain().GetBlockByNumber(sameHeight).Hash()
+	ethBackend.handler.downloader.ProcessMilestone(sameHeight, anchorLocal)
+
+	bogus := mutateHexString(anchorLocal.Hex()[2:])
+
+	verifier := newBorVerifier()
+	ethHandler := (*ethHandler)(ethBackend.handler)
+
+	_, err := verifier.verify(ctx, ethBackend, ethHandler, sameHeight, sameHeight, bogus, false)
+	require.ErrorIs(t, err, errHashMismatch)
+
+	require.Equal(t, headBefore, ethBackend.BlockChain().CurrentBlock().Number.Uint64())
+
+	exists, num, h := ethBackend.handler.downloader.GetWhitelistedMilestone()
+	require.True(t, exists)
+	require.Equal(t, sameHeight, num)
+	require.Equal(t, anchorLocal, h)
+}
+
+// Unattesting whitelist must not short-circuit search: a matching future
+// milestone below end becomes the rewind anchor.
+func TestMilestoneMismatch_FutureMilestoneFallback_RewindsWhenWhitelistUnattested(t *testing.T) {
+	t.Parallel()
+
+	log.SetDefault(log.NewLogger(log.NewTerminalHandlerWithLevel(os.Stderr, log.LevelInfo, true)))
+
+	ctx, cancel := context.WithTimeout(context.Background(), 60*time.Second)
+	defer cancel()
+
+	stack, ethBackend, headBefore := startMinedBorNode(t, 20)
+	defer stack.Close()
+	require.GreaterOrEqual(t, headBefore, uint64(20))
+
+	dl := ethBackend.handler.downloader
+
+	sameHeight := headBefore - 5
+	sameHeightHash := ethBackend.BlockChain().GetBlockByNumber(sameHeight).Hash()
+	dl.ProcessMilestone(sameHeight, sameHeightHash)
+
+	earlier := headBefore - 12
+	earlierHash := ethBackend.BlockChain().GetBlockByNumber(earlier).Hash()
+	dl.ProcessFutureMilestone(earlier, earlierHash)
+
+	bogus := mutateHexString(sameHeightHash.Hex()[2:])
+
+	verifier := newBorVerifier()
+	ethHandler := (*ethHandler)(ethBackend.handler)
+
+	_, err := verifier.verify(ctx, ethBackend, ethHandler, sameHeight, sameHeight, bogus, false)
+	require.ErrorIs(t, err, errHashMismatch)
+
+	require.Equal(t, earlier, ethBackend.BlockChain().CurrentBlock().Number.Uint64())
+	require.Equal(t, earlierHash, ethBackend.BlockChain().CurrentBlock().Hash())
+
+	exists, _, _ := dl.GetWhitelistedMilestone()
+	require.False(t, exists)
+}
+
+// Genesis is a valid attested anchor; rewindTo==0 must not be confused with "unset".
+func TestMilestoneMismatch_GenesisAnchor_RewindsAndKeepsAttested(t *testing.T) {
+	t.Parallel()
+
+	log.SetDefault(log.NewLogger(log.NewTerminalHandlerWithLevel(os.Stderr, log.LevelInfo, true)))
+
+	ctx, cancel := context.WithTimeout(context.Background(), 60*time.Second)
+	defer cancel()
+
+	stack, ethBackend, headBefore := startMinedBorNode(t, 20)
+	defer stack.Close()
+	require.Less(t, headBefore, uint64(126)) // within maxRewindLen
+
+	genesisHash := ethBackend.BlockChain().GetBlockByNumber(0).Hash()
+	ethBackend.handler.downloader.ProcessMilestone(0, genesisHash)
+
+	mismatchEnd := headBefore - 3
+	mismatchStart := mismatchEnd - 1
+	bogus := mutateHexString(ethBackend.BlockChain().GetBlockByNumber(mismatchEnd).Hash().Hex()[2:])
+
+	verifier := newBorVerifier()
+	ethHandler := (*ethHandler)(ethBackend.handler)
+
+	_, err := verifier.verify(ctx, ethBackend, ethHandler, mismatchStart, mismatchEnd, bogus, false)
+	require.ErrorIs(t, err, errHashMismatch)
+
+	require.Equal(t, uint64(0), ethBackend.BlockChain().CurrentBlock().Number.Uint64())
+	require.Equal(t, genesisHash, ethBackend.BlockChain().CurrentBlock().Hash())
+}
+
 func TestMilestoneMismatch_UnknownHash_DoesNotRewind(t *testing.T) {
 	t.Parallel()
 
@@ -541,6 +730,18 @@ func waitForHeadAtLeast(t *testing.T, ethBackend *Ethereum, target uint64, timeo
 	}
 }
 
+// startMinedBorNode mines to target, stops the miner, returns (stack, backend,
+// head). For tests that need head stable across assertions.
+func startMinedBorNode(t *testing.T, target uint64) (*node.Node, *Ethereum, uint64) {
+	t.Helper()
+
+	stack, ethBackend := startBorNode(t, loadBorTestGenesis(t), generateTestKey(t))
+	require.NoError(t, ethBackend.StartMining())
+	waitForHeadAtLeast(t, ethBackend, target, 30*time.Second)
+	ethBackend.StopMining()
+	return stack, ethBackend, ethBackend.BlockChain().CurrentBlock().Number.Uint64()
+}
+
 func generateTestKey(t *testing.T) *ecdsa.PrivateKey {
 	t.Helper()
 	key, err := crypto.GenerateKey()
```

### eth/downloader/bor_downloader_test.go
```diff
@@ -1637,7 +1637,8 @@ func (w *whitelistFake) UpdateFastForwardMilestone(num uint64, hash common.Hash)
 func (w *whitelistFake) GetWhitelistedMilestone() (bool, uint64, common.Hash) {
 	return false, 0, common.Hash{}
 }
-func (w *whitelistFake) PurgeWhitelistedMilestone() {}
+func (w *whitelistFake) PurgeWhitelistedMilestone()    {}
+func (w *whitelistFake) PurgeMilestonesAfter(_ uint64) {}
 
 func (w *whitelistFake) GetCheckpoints(current, sidechainHeader *types.Header, sidechainCheckpoints []*types.Header) (map[uint64]*types.Header, error) {
 	return map[uint64]*types.Header{}, nil
```

### eth/downloader/whitelist/milestone.go
```diff
@@ -40,6 +40,7 @@ type milestoneService interface {
 	UnlockMutex(doLock bool, milestoneId string, endBlockNum uint64, endBlockHash common.Hash)
 	UnlockSprint(endBlockNum uint64)
 	ProcessFutureMilestone(num uint64, hash common.Hash)
+	PurgeAfter(block uint64)
 }
 
 var (
@@ -57,6 +58,9 @@ var (
 
 	// MilestonePeerMeter is a metric for collecting the number of valid peers received
 	MilestonePeerMeter = metrics.NewRegisteredMeter("chain/milestone/isvalidpeer", nil)
+
+	// PurgeAfterDBErrorMeter is a metric for tracking the purge after database errors when deleting stale milestones after a mismatch rewind
+	PurgeAfterDBErrorMeter = metrics.NewRegisteredMeter("chain/milestone/purgeafter/dberror", nil)
 )
 
 // IsValidChain checks the validity of chain by comparing it
@@ -337,6 +341,63 @@ func (m *milestone) processFutureMilestoneLocked(num uint64, hash common.Hash) {
 	}
 }
 
+// PurgeAfter drops whitelist/locked/future-queued entries strictly above block,
+// in memory and on disk. Called after a milestone-mismatch rewind so stale
+// entries from the displaced fork don't reject canonical peers.
+func (m *milestone) PurgeAfter(block uint64) {
+	m.finality.Lock()
+	defer m.finality.Unlock()
+
+	persistedNum, _, persistedErr := rawdb.ReadFinality[*rawdb.Milestone](m.db)
+	diskStale := persistedErr == nil && persistedNum > block
+	memStale := m.doExist && m.Number > block
+	if diskStale || memStale {
+		if err := rawdb.DeleteLastFinality[*rawdb.Milestone](m.db); err != nil {
+			log.Error("PurgeAfter: failed to delete stale whitelisted milestone from db; clearing memory anyway", "err", err)
+			PurgeAfterDBErrorMeter.Mark(1)
+		}
+		if memStale {
+			m.doExist = false
+			m.Number = 0
+			m.Hash = common.Hash{}
+			whitelistedMilestoneMeter.Update(0)
+		}
+	}
+
+	if m.Locked && m.LockedMilestoneNumber > block {
+		m.Locked = false
+		m.LockedMilestoneNumber = 0
+		m.LockedMilestoneHash = common.Hash{}
+		m.purgeMilestoneIDsList()
+		MilestoneIdsLengthMeter.Update(0)
+		if err := rawdb.WriteLockField(m.db, m.Locked, m.LockedMilestoneNumber, m.LockedMilestoneHash, m.LockedMilestoneIDs); err != nil {
+			log.Error("Error clearing stale milestone lock from db", "err", err)
+		}
+	}
+
+	if len(m.FutureMilestoneOrder) > 0 {
+		filteredOrder := m.FutureMilestoneOrder[:0:0]
+		for _, num := range m.FutureMilestoneOrder {
+			if num > block {
+				delete(m.FutureMilestoneList, num)
+			} else {
+				filteredOrder = append(filteredOrder, num)
+			}
+		}
+		if len(filteredOrder) != len(m.FutureMilestoneOrder) {
+			m.FutureMilestoneOrder = filteredOrder
+			if err := rawdb.WriteFutureMilestoneList(m.db, m.FutureMilestoneOrder, m.FutureMilestoneList); err != nil {
+				log.Error("Error persisting trimmed future milestone list to db", "err", err)
+			}
+			var newMax int64
+			if n := len(filteredOrder); n > 0 {
+				newMax = int64(filteredOrder[n-1])
+			}
+			FutureMilestoneMeter.Update(newMax)
+		}
+	}
+}
+
 // enqueueFutureMilestoneLocked assumes m.finality.Lock() is already held.
 func (m *milestone) enqueueFutureMilestoneLocked(key uint64, hash common.Hash) {
 	if _, ok := m.FutureMilestoneList[key]; ok {
```

### eth/downloader/whitelist/milestone_test.go
```diff
@@ -13,6 +13,94 @@ import (
 	"github.com/ethereum/go-ethereum/core/types"
 )
 
+func TestPurgeAfter(t *testing.T) {
+	db := rawdb.NewMemoryDatabase()
+	svc := NewService(db, false, 0)
+
+	m, ok := svc.milestoneService.(*milestone)
+	if !ok {
+		t.Fatalf("expected milestoneService to be *milestone, got %T", svc.milestoneService)
+	}
+
+	hashAt := func(n uint64) common.Hash { return common.Hash{byte(n)} }
+
+	m.Process(100, hashAt(100))
+	m.ProcessFutureMilestone(80, hashAt(80))
+	m.ProcessFutureMilestone(110, hashAt(110))
+	m.ProcessFutureMilestone(130, hashAt(130))
+	// Lock state set after the ProcessFutureMilestone calls: those clear the
+	// lock when num >= LockedMilestoneNumber.
+	m.finality.Lock()
+	m.Locked = true
+	m.LockedMilestoneNumber = 120
+	m.LockedMilestoneHash = hashAt(120)
+	m.LockedMilestoneIDs = map[string]struct{}{"id1": {}}
+	_ = rawdb.WriteLockField(db, m.Locked, m.LockedMilestoneNumber, m.LockedMilestoneHash, m.LockedMilestoneIDs)
+	m.finality.Unlock()
+
+	m.PurgeAfter(90)
+
+	m.finality.RLock()
+	if m.doExist {
+		t.Fatalf("doExist must be false after purge")
+	}
+	if _, _, err := rawdb.ReadFinality[*rawdb.Milestone](db); err == nil {
+		t.Fatalf("persisted whitelist row must be deleted")
+	}
+	if m.Locked || m.LockedMilestoneNumber != 0 || len(m.LockedMilestoneIDs) != 0 {
+		t.Fatalf("lock state must be cleared")
+	}
+	if _, ok := m.FutureMilestoneList[80]; !ok {
+		t.Fatalf("future entry at 80 must be kept")
+	}
+	if _, ok := m.FutureMilestoneList[110]; ok {
+		t.Fatalf("future entry at 110 must be evicted")
+	}
+	if _, ok := m.FutureMilestoneList[130]; ok {
+		t.Fatalf("future entry at 130 must be evicted")
+	}
+	if len(m.FutureMilestoneOrder) != 1 || m.FutureMilestoneOrder[0] != 80 {
+		t.Fatalf("order must contain only 80, got %v", m.FutureMilestoneOrder)
+	}
+	m.finality.RUnlock()
+
+	// Pins the DB-delete-before-memory-clear ordering: Get's DB fallback would
+	// otherwise resurrect the row on the next call.
+	if exists, _, _ := m.Get(); exists {
+		t.Fatalf("Get() must not resurrect purged whitelist")
+	}
+}
+
+func TestPurgeAfter_MemoryFalseDiskStale(t *testing.T) {
+	db := rawdb.NewMemoryDatabase()
+	svc := NewService(db, false, 0)
+
+	m, ok := svc.milestoneService.(*milestone)
+	if !ok {
+		t.Fatalf("expected milestoneService to be *milestone, got %T", svc.milestoneService)
+	}
+
+	hashAt := func(n uint64) common.Hash { return common.Hash{byte(n)} }
+
+	if err := rawdb.WriteLastFinality[*rawdb.Milestone](db, 100, hashAt(100)); err != nil {
+		t.Fatalf("seed: %v", err)
+	}
+	m.finality.Lock()
+	m.doExist = false
+	m.Number = 0
+	m.Hash = common.Hash{}
+	m.finality.Unlock()
+
+	m.PurgeAfter(50)
+
+	if _, _, err := rawdb.ReadFinality[*rawdb.Milestone](db); err == nil {
+		t.Fatalf("stale on-disk row must be deleted")
+	}
+	if exists, _, _ := m.Get(); exists {
+		t.Fatalf("Get() must not resurrect")
+	}
+}
+
 func TestUnlockSprintThreshold(t *testing.T) {
 	db := rawdb.NewMemoryDatabase()
 	svc := NewService(db, false, 0)
```

### eth/downloader/whitelist/service.go
```diff
@@ -5,6 +5,7 @@ import (
 	"fmt"
 	"math"
 	"sync"
+	"sync/atomic"
 
 	"github.com/ethereum/go-ethereum/common"
 	"github.com/ethereum/go-ethereum/core/rawdb"
@@ -35,9 +36,10 @@ type Service struct {
 
 	disableBlindForkValidation bool   // Flag to disable additional fork validation and accept blind forks without tracing back to last whitelisted entry
 	maxForkCorrectnessLimit    uint64 // Maximum number of blocks to iterate backwards for fork correctness check
-	lastValidForkBlock         uint64 // Last known valid block for fork correctness check
-	forkValidationCache        map[common.Hash]bool
-	forkValidationCacheMu      sync.RWMutex
+
+	lastValidForkBlock    atomic.Uint64
+	forkValidationCache   map[common.Hash]bool
+	forkValidationCacheMu sync.RWMutex
 }
 
 func NewService(db ethdb.Database, disableBlindForkValidation bool, maxBlindForkValidationLimit uint64) *Service {
@@ -131,7 +133,6 @@ func NewService(db ethdb.Database, disableBlindForkValidation bool, maxBlindFork
 		},
 		disableBlindForkValidation: disableBlindForkValidation,
 		maxForkCorrectnessLimit:    maxBlindForkValidationLimit,
-		lastValidForkBlock:         0,
 		forkValidationCache:        make(map[common.Hash]bool, forkValidationCacheSize),
 	}
 }
@@ -169,6 +170,23 @@ func (s *Service) PurgeWhitelistedMilestone() {
 	s.milestoneService.Purge()
 }
 
+// PurgeMilestonesAfter drops milestone state above block, clears the fork
+// validation cache, and caps lastValidForkBlock at block. checkForkCorrectness
+// uses max(milestoneNumber, lastValidForkBlock) as its canonical bound, so a
+// stale lastValidForkBlock would blind-accept peer chains past the rewind anchor.
+func (s *Service) PurgeMilestonesAfter(block uint64) {
+	s.milestoneService.PurgeAfter(block)
+	s.forkValidationCacheMu.Lock()
+	clear(s.forkValidationCache)
+	s.forkValidationCacheMu.Unlock()
+	for {
+		cur := s.lastValidForkBlock.Load()
+		if cur <= block || s.lastValidForkBlock.CompareAndSwap(cur, block) {
+			break
+		}
+	}
+}
+
 func (s *Service) GetWhitelistedCheckpoint() (bool, uint64, common.Hash) {
 	return s.checkpointService.Get()
 }
@@ -243,8 +261,8 @@ func (s *Service) checkForkCorrectness(chain []*types.Header) bool {
 	}
 
 	var lastKnownValidBlock uint64 = number
-	if s.lastValidForkBlock > number {
-		lastKnownValidBlock = s.lastValidForkBlock
+	if v := s.lastValidForkBlock.Load(); v > number {
+		lastKnownValidBlock = v
 	}
 
 	// Blind accept the chain if we've to iterate more than `maxForkCorrectnessLimit` blocks
@@ -275,7 +293,7 @@ func (s *Service) checkForkCorrectness(chain []*types.Header) bool {
 				// Cache suggests that this fork is already validated. Accept the fork
 				// and update the cache.
 				s.updateForkValidationCache(blocksChecked)
-				s.lastValidForkBlock = lastHeaderNumber
+				s.lastValidForkBlock.Store(lastHeaderNumber)
 				return true
 			}
 			// Fetch the parent block by number and hash
@@ -295,7 +313,7 @@ func (s *Service) checkForkCorrectness(chain []*types.Header) bool {
 					// If valid, cache the blocks checked already to avoid re-checking
 					// them in next import.
 					s.updateForkValidationCache(blocksChecked)
-					s.lastValidForkBlock = lastHeaderNumber
+					s.lastValidForkBlock.Store(lastHeaderNumber)
 				} else {
 					log.Info("Rejecting invalid fork after validating against last whitelisted entry", "number", number, "expected", hash, "got", header.Hash())
 				}
```

### eth/downloader/whitelist/service_test.go
```diff
@@ -73,7 +73,6 @@ func NewMockService(db ethdb.Database) *Service {
 			MaxCapacity:          10,
 		},
 		maxForkCorrectnessLimit: 10,
-		lastValidForkBlock:      0,
 		forkValidationCache:     make(map[common.Hash]bool, 10),
 	}
 }
@@ -1375,7 +1374,7 @@ func TestForkCorrectness(t *testing.T) {
 
 		res := s.checkForkCorrectness(chainA[16:]) // 11 blocks ahead of last checkpoint
 		require.Equal(t, true, res, "expected chain to be valid")
-		require.Equal(t, uint64(0), s.lastValidForkBlock, "expected last known valid block to be 0")
+		require.Equal(t, uint64(0), s.lastValidForkBlock.Load(), "expected last known valid block to be 0")
 		require.Equal(t, 0, len(s.forkValidationCache), "expected no entries in cache")
 	})
 
@@ -1385,7 +1384,7 @@ func TestForkCorrectness(t *testing.T) {
 
 		res := s.checkForkCorrectness(chainA[16:]) // 12 blocks ahead of last milestone
 		require.Equal(t, true, res, "expected chain to be valid")
-		require.Equal(t, uint64(0), s.lastValidForkBlock, "expected last known valid block to be 0")
+		require.Equal(t, uint64(0), s.lastValidForkBlock.Load(), "expected last known valid block to be 0")
 		require.Equal(t, 0, len(s.forkValidationCache), "expected no entries in cache")
 	})
 
@@ -1395,12 +1394,12 @@ func TestForkCorrectness(t *testing.T) {
 
 		res := s.checkForkCorrectness(chainA[16:]) // 12 blocks ahead of last milestone
 		require.Equal(t, true, res, "expected chain to be valid")
-		require.Equal(t, uint64(0), s.lastValidForkBlock, "expected last known valid block to be 0")
+		require.Equal(t, uint64(0), s.lastValidForkBlock.Load(), "expected last known valid block to be 0")
 		require.Equal(t, 0, len(s.forkValidationCache), "expected no entries in cache")
 	})
 
 	t.Run("long fork: both milestone and checkpoint exist but last known block is recent", func(t *testing.T) {
-		s.lastValidForkBlock = 6 // 1 block ahead of last checkpoint
+		s.lastValidForkBlock.Store(6) // 1 block ahead of last checkpoint
 
 		res := s.checkForkCorrectness(chainA[17:]) // 11 blocks ahead of last known block
 		require.Equal(t, true, res, "expected chain to be valid")
@@ -1414,7 +1413,7 @@ func TestForkCorrectness(t *testing.T) {
 		res := s.checkForkCorrectness(chainA[17:]) // 11 blocks ahead of last known block
 		require.Equal(t, true, res, "expected chain to be valid")
 		require.Equal(t, 0, len(s.forkValidationCache), "expected no entries in cache")
-		s.lastValidForkBlock = 0
+		s.lastValidForkBlock.Store(0)
 	})
 
 	// Create a mock chain linking back to last block
@@ -1429,7 +1428,7 @@ func TestForkCorrectness(t *testing.T) {
 
 		res := s.checkForkCorrectness(chain1)
 		require.Equal(t, true, res, "expected chain to be valid")
-		require.Equal(t, chain1[1].Number.Uint64(), s.lastValidForkBlock, "expected last known valid block to be updated")
+		require.Equal(t, chain1[1].Number.Uint64(), s.lastValidForkBlock.Load(), "expected last known valid block to be updated")
 		require.Equal(t, 2, len(s.forkValidationCache), "expected two entries in cache")
 		require.Equal(t, true, s.forkValidationCache[chain1[0].Hash()], "expected cache to have valid entry")
 		require.Equal(t, true, s.forkValidationCache[chain1[1].Hash()], "expected cache to have valid entry")
@@ -1444,7 +1443,7 @@ func TestForkCorrectness(t *testing.T) {
 	t.Run("incoming chain further ahead of last chain", func(t *testing.T) {
 		res := s.checkForkCorrectness(chain2)
 		require.Equal(t, true, res, "expected chain to be valid")
-		require.Equal(t, chain2[1].Number.Uint64(), s.lastValidForkBlock, "expected last known valid block to be updated")
+		require.Equal(t, chain2[1].Number.Uint64(), s.lastValidForkBlock.Load(), "expected last known valid block to be updated")
 		require.Equal(t, 4, len(s.forkValidationCache), "expected four entries in cache") // block 21, 22, 23, 24 should be present in cache
 		require.Equal(t, true, s.forkValidationCache[chain1[0].Hash()], "expected cache to have valid entry: block 21")
 		require.Equal(t, true, s.forkValidationCache[chain1[1].Hash()], "expected cache to have valid entry: block 22")
@@ -1468,7 +1467,7 @@ func TestForkCorrectness(t *testing.T) {
 
 		// The last valid fork block shouldn't be updated as we couldn't verify the chain
 		// due to missing header. The cache except for the explicit deletion should be intact.
-		require.Equal(t, chain2[1].Number.Uint64(), s.lastValidForkBlock, "expected last known valid block to be unchanged")
+		require.Equal(t, chain2[1].Number.Uint64(), s.lastValidForkBlock.Load(), "expected last known valid block to be unchanged")
 		require.Equal(t, 3, len(s.forkValidationCache), "expected three entries in cache") // block 21, 22, 23 should be present in cache
 		require.Equal(t, true, s.forkValidationCache[chain1[0].Hash()], "expected cache to have valid entry: block 21")
 		require.Equal(t, true, s.forkValidationCache[chain1[1].Hash()], "expected cache to have valid entry: block 22")
@@ -1486,7 +1485,7 @@ func TestForkCorrectness(t *testing.T) {
 		// The fork should be valid as block 24 is present in cache (even though header is not available)
 		res := s.checkForkCorrectness(chain3)
 		require.Equal(t, true, res, "expected chain to be valid")
-		require.Equal(t, chain3[1].Number.Uint64(), s.lastValidForkBlock, "expected last known valid block to be updates") // block 26
+		require.Equal(t, chain3[1].Number.Uint64(), s.lastValidForkBlock.Load(), "expected last known valid block to be updates") // block 26
 
 		require.Equal(t, 6, len(s.forkValidationCache), "expected six entries in cache") // block 21, 22, 23, 24, 25, 26 should be present in cache
 		require.Equal(t, true, s.forkValidationCache[chain1[0].Hash()], "expected cache to have valid entry: block 21")
@@ -1531,7 +1530,7 @@ func TestForkCorrectness(t *testing.T) {
 		res := s.checkForkCorrectness(chain4[1:])
 		require.Equal(t, false, res, "expected chain to be invalid due to mismatch with milestone")
 		require.Equal(t, 0, len(s.forkValidationCache), "expected no entries in cache")
-		require.Equal(t, chain3[1].Number.Uint64(), s.lastValidForkBlock, "expected last known valid block to be unchanged")
+		require.Equal(t, chain3[1].Number.Uint64(), s.lastValidForkBlock.Load(), "expected last known valid block to be unchanged")
 	})
 }
 
```

### interfaces.go
```diff
@@ -303,6 +303,7 @@ type ChainValidator interface {
 	ProcessFutureMilestone(num uint64, hash common.Hash)
 	PurgeWhitelistedCheckpoint()
 	PurgeWhitelistedMilestone()
+	PurgeMilestonesAfter(block uint64)
 
 	LockMutex(endBlockNum uint64) bool
 	UnlockMutex(doLock bool, milestoneId string, endBlockNum uint64, endBlockHash common.Hash)
```
