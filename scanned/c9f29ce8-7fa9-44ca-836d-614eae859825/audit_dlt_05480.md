# [?] core/vote: prevent vote pool DOS (#684)

## Summary
Severity: Unknown
Chain: Ronin
Component: axieinfinity/ronin
Published: 2025-02-13
Source: https://github.com/axieinfinity/ronin-archive/commit/3d30c056636df6e9b97a25eeb06d03699ee5f8ed
Type: security-commit

## Details
core/vote: prevent vote pool DOS (#684)

* core/vote: only track originated peer if vote is valid

* core/vote: prune peer feature vote counter if reached threshold

* core/vote: blocking put vote flow, verify vote target number

## Patch
### core/vote/vote_pool.go
```diff
@@ -17,13 +17,11 @@ import (
 const (
 	maxFutureVoteAmountPerBlock = 64
 	maxFutureVotePerPeer        = 25
-
-	voteBufferForPut = 256
+	voteBufferForPut            = 256
 	// votes in the range (currentBlockNum-256,currentBlockNum+11] will be stored
 	lowerLimitOfVoteBlockNumber = 256
 	upperLimitOfVoteBlockNumber = 11 // refer to fetcher.maxUncleDist
-
-	chainHeadChanSize = 10 // chainHeadChanSize is the size of channel listening to ChainHeadEvent.
+	chainHeadChanSize           = 10 // chainHeadChanSize is the size of channel listening to ChainHeadEvent.
 
 	fetchCheckFrequency = 1 * time.Millisecond
 	fetchRetry          = 500
@@ -67,6 +65,7 @@ type VotePool struct {
 	maxCurVoteAmountPerBlock int
 
 	numFutureVotePerPeer map[string]uint64      // number of queued votes per peer
+	lastFutureVoteBlock  map[string]uint64      // last block that peer has future vote
 	originatedFrom       map[common.Hash]string // mapping from vote hash to the sender
 	justifiedBlockNumber uint64
 }
@@ -89,6 +88,7 @@ func NewVotePool(
 		engine:                   engine,
 		maxCurVoteAmountPerBlock: maxCurVoteAmountPerBlock,
 		numFutureVotePerPeer:     make(map[string]uint64),
+		lastFutureVoteBlock:      make(map[string]uint64),
 		originatedFrom:           make(map[common.Hash]string),
 	}
 
@@ -126,11 +126,7 @@ func (pool *VotePool) loop() {
 }
 
 func (pool *VotePool) PutVote(peer string, vote *types.VoteEnvelope) {
-	select {
-	case pool.votesCh <- &voteWithPeer{vote: vote, peer: peer}:
-	default:
-		log.Debug("Failed to put vote into vote pool")
-	}
+	pool.votesCh <- &voteWithPeer{vote: vote, peer: peer}
 }
 
 func (pool *VotePool) putIntoVotePool(voteWithPeerInfo *voteWithPeer) bool {
@@ -157,11 +153,11 @@ func (pool *VotePool) putIntoVotePool(voteWithPeerInfo *voteWithPeer) bool {
 	}
 
 	voteHash := vote.Hash()
+	isFutureVote := false
 	if _, ok := pool.originatedFrom[voteHash]; ok {
 		log.Debug("Vote pool already contained the same vote", "voteHash", voteHash)
 		return false
 	}
-	pool.originatedFrom[voteHash] = peer
 
 	voteData := &types.VoteData{
 		TargetNumber: targetNumber,
@@ -170,7 +166,6 @@ func (pool *VotePool) putIntoVotePool(voteWithPeerInfo *voteWithPeer) bool {
 
 	var votes map[common.Hash]*VoteBox
 	var votesPq *votesPriorityQueue
-	isFutureVote := false
 
 	voteBlock := pool.chain.GetHeaderByHash(targetHash)
 	if voteBlock == nil {
@@ -180,6 +175,11 @@ func (pool *VotePool) putIntoVotePool(voteWithPeerInfo *voteWithPeer) bool {
 	} else {
 		votes = pool.curVotes
 		votesPq = pool.curVotesPq
+
+		// Verify if the vote target number is the same as the vote block number
+		if voteBlock.Number != nil && voteBlock.Number.Uint64() != targetNumber {
+			return false
+		}
 	}
 
 	if isFutureVote {
@@ -188,13 +188,9 @@ func (pool *VotePool) putIntoVotePool(voteWithPeerInfo *voteWithPeer) bool {
 		if pool.numFutureVotePerPeer[peer] >= maxFutureVotePerPeer {
 			return false
 		}
-		pool.numFutureVotePerPeer[peer]++
 	}
 
 	if ok := pool.basicVerify(vote, headNumber, votes, isFutureVote, voteHash); !ok {
-		if isFutureVote {
-			pool.numFutureVotePerPeer[peer]--
-		}
 		return false
 	}
 
@@ -210,7 +206,15 @@ func (pool *VotePool) putIntoVotePool(voteWithPeerInfo *voteWithPeer) bool {
 	}
 
 	pool.putVote(votes, votesPq, vote, voteData, voteHash, isFutureVote)
-
+	pool.originatedFrom[voteHash] = peer
+	// Update the peer feature vote counter, and its last block for pruning
+	if isFutureVote {
+		pool.numFutureVotePerPeer[peer]++
+		lastBlock := pool.lastFutureVoteBlock[peer]
+		if lastBlock < targetNumber {
+			pool.lastFutureVoteBlock[peer] = targetNumber
+		}
+	}
 	return true
 }
 
@@ -357,11 +361,25 @@ func (pool *VotePool) pruneVote(
 	}
 }
 
+func (pool *VotePool) pruneFutureVoteCounter(latestBlockNumber uint64) {
+	// Only keep track of couter for peer has future vote > currentBlockNum-lowerLimitOfVoteBlockNumber
+	thresholdBlock := max(int64(latestBlockNumber)-lowerLimitOfVoteBlockNumber, 0)
+	for peer, lastBlock := range pool.lastFutureVoteBlock {
+		if lastBlock <= uint64(thresholdBlock) {
+			log.Debug("Prune future vote counter for peer", "peer", peer,
+				"lastBlock", lastBlock, "thresholdBlock", thresholdBlock, "currentBlock", latestBlockNumber)
+			delete(pool.numFutureVotePerPeer, peer)
+			delete(pool.lastFutureVoteBlock, peer)
+		}
+	}
+}
+
 // Prune old data of curVotes and futureVotes
 // The caller must hold the pool mutex
 func (pool *VotePool) prune(latestBlockNumber uint64) {
 	pool.pruneVote(latestBlockNumber, pool.curVotes, pool.curVotesPq, false)
 	pool.pruneVote(latestBlockNumber, pool.futureVotes, pool.futureVotesPq, true)
+	pool.pruneFutureVoteCounter(latestBlockNumber)
 }
 
 // GetVotes as batch.
@@ -444,6 +462,13 @@ func (pool *VotePool) stats() (int, int, int, int) {
 	return len(pool.curVotes), pool.curVotesPq.Len(), len(pool.futureVotes), pool.futureVotesPq.Len()
 }
 
+func (pool *VotePool) peerTrackStats() (int, int) {
+	pool.mu.RLock()
+	defer pool.mu.RUnlock()
+
+	return len(pool.numFutureVotePerPeer), len(pool.lastFutureVoteBlock)
+}
+
 func (pool *VotePool) getNumberOfFutureVoteByPeer(peer string) uint64 {
 	pool.mu.RLock()
 	defer pool.mu.RUnlock()
```

### core/vote/vote_pool_test.go
```diff
@@ -479,6 +479,71 @@ func TestVotePoolDosProtection(t *testing.T) {
 	}
 }
 
+func TestVotePoolPruneFutureVoteCounter(t *testing.T) {
+	// Create a database pre-initialize with a genesis block
+	db := rawdb.NewMemoryDatabase()
+	genesis := (&core.Genesis{
+		Config:  params.TestChainConfig,
+		Alloc:   core.GenesisAlloc{testAddr: {Balance: big.NewInt(1000000)}},
+		BaseFee: big.NewInt(params.InitialBaseFee),
+	}).MustCommit(db)
+	chain, _ := core.NewBlockChain(db, nil, params.TestChainConfig, ethash.NewFullFaker(), vm.Config{}, nil, nil)
+	bs, _ := core.GenerateChain(params.TestChainConfig, genesis, ethash.NewFaker(), db, lowerLimitOfVoteBlockNumber+1, nil, true)
+	if _, err := chain.InsertChain(bs[:1], nil); err != nil {
+		panic(err)
+	}
+	mockEngine := &mockPOSA{}
+
+	// Create vote pool
+	voteNum := lowerLimitOfVoteBlockNumber
+	votePool := NewVotePool(chain, mockEngine, voteNum)
+	secretKey, err := bls.RandKey()
+	if err != nil {
+		t.Fatalf("Failed to create secret key, err %s", err)
+	}
+
+	// Test prune future vote counter for malicious peer
+	for i := 0; i < voteNum; i++ {
+		vote := generateVote(1, common.BigToHash(big.NewInt(int64(i))), secretKey)
+		votePool.PutVote(fmt.Sprintf("XXXX-%d", i), vote)
+		time.Sleep(100 * time.Millisecond)
+	}
+
+	currentPeerCouter, currentPeerTrackLength := votePool.peerTrackStats()
+	if currentPeerCouter != voteNum {
+		t.Fatalf("Current peer counter, expect %d have %d", voteNum, currentPeerCouter)
+	}
+	if currentPeerTrackLength != voteNum {
+		t.Fatalf("Current peer track length, expect %d have %d", voteNum, currentPeerTrackLength)
+	}
+
+	if _, err := chain.InsertChain(bs[1:voteNum-1], nil); err != nil {
+		panic(err)
+	}
+
+	time.Sleep(500 * time.Millisecond)
+	currentPeerCouter, currentPeerTrackLength = votePool.peerTrackStats()
+	if currentPeerCouter != voteNum {
+		t.Fatalf("Current peer counter, expect %d have %d", voteNum, currentPeerCouter)
+	}
+	if currentPeerTrackLength != voteNum {
+		t.Fatalf("Current peer track length, expect %d have %d", voteNum, currentPeerTrackLength)
+	}
+
+	if _, err := chain.InsertChain(bs[voteNum-1:], nil); err != nil {
+		panic(err)
+	}
+
+	time.Sleep(100 * time.Millisecond)
+	currentPeerCouter, currentPeerTrackLength = votePool.peerTrackStats()
+	if currentPeerCouter != 0 {
+		t.Fatalf("Current peer counter, expect %d have %d", 0, currentPeerCouter)
+	}
+	if currentPeerTrackLength != 0 {
+		t.Fatalf("Current peer track length, expect %d have %d", 0, currentPeerTrackLength)
+	}
+}
+
 type mockPOSAv2 struct {
 	consensus.FastFinalityPoSA
 }
```
