# [?] consensus/parlia, core: fix race condition in early finalization (#3547)

## Summary
Severity: Unknown
Chain: BNB Chain
Component: bnb-chain/bsc
Published: 2026-02-04
Source: https://github.com/bnb-chain/bsc/commit/6c103a841f19e6739a56b24d3937358b039e2434
Type: security-commit

## Details
consensus/parlia, core: fix race condition in early finalization (#3547)

Co-authored-by: Cursor <cursoragent@cursor.com>

## Patch
### consensus/parlia/parlia.go
```diff
@@ -265,10 +265,6 @@ type Parlia struct {
 	slashABI                   abi.ABI
 	stakeHubABI                abi.ABI
 
-	// finalizedNotified tracks blocks that have already triggered early finalization notification
-	// to avoid duplicate notifications
-	finalizedNotified *lru.Cache[common.Hash, struct{}]
-
 	// The fields below are for testing only
 	fakeDiff bool // Skip difficulty verifications
 }
@@ -309,7 +305,6 @@ func New(
 		recentSnaps:                lru.NewCache[common.Hash, *Snapshot](inMemorySnapshots),
 		recentHeaders:              lru.NewCache[string, common.Hash](inMemoryHeaders),
 		signatures:                 lru.NewCache[common.Hash, common.Address](inMemorySignatures),
-		finalizedNotified:          lru.NewCache[common.Hash, struct{}](inMemorySnapshots),
 		validatorSetABIBeforeLuban: vABIBeforeLuban,
 		validatorSetABI:            vABI,
 		slashABI:                   sABI,
@@ -2323,26 +2318,18 @@ func (p *Parlia) GetFinalizedHeader(chain consensus.ChainHeaderReader, header *t
 // CheckFinalityAndNotify checks if votes for the target block have reached quorum,
 // and if so, notifies the blockchain of early finalization via the notifyFn callback.
 func (p *Parlia) CheckFinalityAndNotify(chain consensus.ChainHeaderReader, targetBlockHash common.Hash, notifyFn func(finalizedHeader *types.Header)) {
-	// Skip if already notified for this block
-	if _, ok := p.finalizedNotified.Get(targetBlockHash); ok {
+	// Get target block header directly by hash (don't rely on currentHeader which may have moved forward)
+	targetHeader := chain.GetHeaderByHash(targetBlockHash)
+	if targetHeader == nil {
 		return
 	}
 
-	// Get target block header
-	currentHeader := chain.CurrentHeader()
-	if currentHeader == nil || currentHeader.Hash() != targetBlockHash {
-		return
-	}
-
-	finalizedHeader := p.GetFinalizedHeader(chain, currentHeader)
+	finalizedHeader := p.GetFinalizedHeader(chain, targetHeader)
 	if finalizedHeader == nil || finalizedHeader.Number.Uint64() == 0 {
 		return
 	}
 
-	// Mark as notified to avoid duplicate notifications
-	p.finalizedNotified.Add(targetBlockHash, struct{}{})
-
-	// Notify via callback
+	// Notify via callback (NotifyFinalized has its own deduplication logic)
 	notifyFn(finalizedHeader)
 }
 
```

### core/blockchain_reader.go
```diff
@@ -68,6 +68,12 @@ func (bc *BlockChain) CurrentFinalBlock() *types.Header {
 	return nil
 }
 
+// HighestNotifiedFinal retrieves the highest finalized block that has been notified.
+// This is used for deduplication in early finalization checks.
+func (bc *BlockChain) HighestNotifiedFinal() *types.Header {
+	return bc.highestNotifiedFinal.Load()
+}
+
 // CurrentSafeBlock retrieves the current safe block of the canonical
 // chain. The block is retrieved from the blockchain's internal cache.
 func (bc *BlockChain) CurrentSafeBlock() *types.Header {
```

### core/vote/vote_pool.go
```diff
@@ -224,9 +224,10 @@ func (pool *VotePool) putVote(m map[common.Hash]*VoteBox, votesPq *votesPriority
 		localFutureVotesCounter.Inc(1)
 	} else {
 		localCurVotesCounter.Inc(1)
-		// Use goroutine to avoid deadlock: CheckFinalityAndNotify -> GetFinalizedHeader -> FetchVotesByBlockHash
-		// requires RLock, but we're holding Lock here.
-		go pool.engine.CheckFinalityAndNotify(pool.chain, targetHash, pool.chain.NotifyFinalized)
+		// Skip if target block is already finalized and notified
+		if highestNotified := pool.chain.HighestNotifiedFinal(); highestNotified == nil || targetNumber > highestNotified.Number.Uint64()+1 {
+			go pool.engine.CheckFinalityAndNotify(pool.chain, targetHash, pool.chain.NotifyFinalized)
+		}
 	}
 	localReceivedVotesGauge.Update(int64(pool.receivedVotes.Cardinality()))
 }
```
