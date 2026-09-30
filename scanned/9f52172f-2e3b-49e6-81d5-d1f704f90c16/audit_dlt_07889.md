# [?] core/vote: fix deadlock in votepool when stop client (#3631)

## Summary
Severity: Unknown
Chain: BNB Chain
Component: bnb-chain/bsc
Published: 2026-04-07
Source: https://github.com/bnb-chain/bsc/commit/b0255ef705ef2e5c18416fbb8e5da6e3fc092738
Type: security-commit

## Details
core/vote: fix deadlock in votepool when stop client (#3631)

## Patch
### core/vote/vote_pool.go
```diff
@@ -78,6 +78,7 @@ type VotePool struct {
 	highestVerifiedBlockSub event.Subscription
 
 	votesCh chan *types.VoteEnvelope
+	quit    chan struct{}
 
 	engine consensus.PoSA
 }
@@ -94,6 +95,7 @@ func NewVotePool(chain *core.BlockChain, engine consensus.PoSA) *VotePool {
 		futureVotesPq:          &votesPriorityQueue{},
 		highestVerifiedBlockCh: make(chan core.HighestVerifiedBlockEvent, highestVerifiedBlockChanSize),
 		votesCh:                make(chan *types.VoteEnvelope, voteBufferForPut),
+		quit:                   make(chan struct{}),
 		engine:                 engine,
 	}
 
@@ -110,6 +112,8 @@ func (pool *VotePool) loop() {
 
 	for {
 		select {
+		case <-pool.quit:
+			return
 		// Handle ChainHeadEvent.
 		case ev := <-pool.highestVerifiedBlockCh:
 			if ev.Header != nil {
@@ -128,7 +132,11 @@ func (pool *VotePool) loop() {
 }
 
 func (pool *VotePool) PutVote(vote *types.VoteEnvelope) {
-	pool.votesCh <- vote
+	select {
+	case pool.votesCh <- vote:
+	default:
+		log.Warn("VotePool channel full, vote dropped", "hash", vote.Hash())
+	}
 }
 
 func (pool *VotePool) putIntoVotePool(vote *types.VoteEnvelope) bool {
@@ -399,6 +407,11 @@ func (pool *VotePool) basicVerify(vote *types.VoteEnvelope, headNumber uint64, m
 	return true
 }
 
+func (pool *VotePool) Stop() {
+	close(pool.quit)
+	pool.scope.Close()
+}
+
 func (pq votesPriorityQueue) Less(i, j int) bool {
 	return pq[i].TargetNumber < pq[j].TargetNumber
 }
```

### eth/backend.go
```diff
@@ -1016,6 +1016,9 @@ func (s *Ethereum) Stop() error {
 	if s.miner.Mining() {
 		s.miner.TryWaitProposalDoneWhenStopping()
 	}
+	if s.votePool != nil {
+		s.votePool.Stop()
+	}
 	// Stop all the peer-related stuff first.
 	s.discmix.Close()
 	s.dropper.Stop()
```
