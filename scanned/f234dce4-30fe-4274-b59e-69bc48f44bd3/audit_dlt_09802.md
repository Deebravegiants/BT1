# [?] Fixed data race. (#4559)

## Summary
Severity: Unknown
Chain: Harmony
Component: harmony-one/harmony
Published: 2023-11-10
Source: https://github.com/harmony-one/harmony/commit/6f7a04799d401c6126b344bc3c6978e9af82acf8
Type: security-commit

## Details
Fixed data race. (#4559)

## Patch
### consensus/consensus_service.go
```diff
@@ -627,14 +627,18 @@ func (consensus *Consensus) selfCommit(payload []byte) error {
 // NumSignaturesIncludedInBlock returns the number of signatures included in the block
 func (consensus *Consensus) NumSignaturesIncludedInBlock(block *types.Block) uint32 {
 	count := uint32(0)
+	consensus.mutex.Lock()
 	members := consensus.Decider.Participants()
+	pubKeys := consensus.getPublicKeys()
+	consensus.mutex.Unlock()
+
 	// TODO(audit): do not reconstruct the Mask
 	mask := bls.NewMask(members)
 	err := mask.SetMask(block.Header().LastCommitBitmap())
 	if err != nil {
 		return count
 	}
-	for _, key := range consensus.GetPublicKeys() {
+	for _, key := range pubKeys {
 		if ok, err := mask.KeyEnabled(key.Bytes); err == nil && ok {
 			count++
 		}
```

### consensus/consensus_v2.go
```diff
@@ -572,19 +572,19 @@ func (consensus *Consensus) preCommitAndPropose(blk *types.Block) error {
 		if _, err := consensus.Blockchain().InsertChain([]*types.Block{blk}, !consensus.FBFTLog().IsBlockVerified(blk.Hash())); err != nil {
 			switch {
 			case errors.Is(err, core.ErrKnownBlock):
-				consensus.getLogger().Info().Msg("[preCommitAndPropose] Block already known")
+				consensus.GetLogger().Info().Msg("[preCommitAndPropose] Block already known")
 			default:
-				consensus.getLogger().Error().Err(err).Msg("[preCommitAndPropose] Failed to add block to chain")
+				consensus.GetLogger().Error().Err(err).Msg("[preCommitAndPropose] Failed to add block to chain")
 				return
 			}
 		}
-
+		consensus.mutex.Lock()
 		consensus.getLogger().Info().Msg("[preCommitAndPropose] Start consensus timer")
 		consensus.consensusTimeout[timeoutConsensus].Start()
 
 		// Send signal to Node to propose the new block for consensus
 		consensus.getLogger().Info().Msg("[preCommitAndPropose] sending block proposal signal")
-
+		consensus.mutex.Unlock()
 		consensus.ReadySignal(AsyncProposal)
 	}()
 
```

### core/blockchain_impl.go
```diff
@@ -1646,6 +1646,8 @@ func (bc *BlockChainImpl) InsertChain(chain types.Blocks, verifyHeaders bool) (i
 	}
 
 	prevHash := bc.CurrentBlock().Hash()
+	bc.chainmu.Lock()
+	defer bc.chainmu.Unlock()
 	n, events, logs, err := bc.insertChain(chain, verifyHeaders)
 	bc.PostChainEvents(events, logs)
 	if err == nil {
@@ -1699,9 +1701,6 @@ func (bc *BlockChainImpl) insertChain(chain types.Blocks, verifyHeaders bool) (i
 		}
 	}
 
-	bc.chainmu.Lock()
-	defer bc.chainmu.Unlock()
-
 	// A queued approach to delivering events. This is generally
 	// faster than direct delivery and requires much less mutex
 	// acquiring.
@@ -1801,9 +1800,7 @@ func (bc *BlockChainImpl) insertChain(chain types.Blocks, verifyHeaders bool) (i
 			// Prune in case non-empty winner chain
 			if len(winner) > 0 {
 				// Import all the pruned blocks to make the state available
-				bc.chainmu.Unlock()
 				_, evs, logs, err := bc.insertChain(winner, true /* verifyHeaders */)
-				bc.chainmu.Lock()
 				events, coalescedLogs = evs, logs
 
 				if err != nil {
```

### p2p/stream/common/streammanager/streammanager.go
```diff
@@ -139,8 +139,8 @@ func (sm *streamManager) loop() {
 				discCancel() // cancel last discovery
 			}
 			discCtx, discCancel = context.WithCancel(sm.ctx)
-			go func() {
-				discovered, err := sm.discoverAndSetupStream(discCtx)
+			go func(ctx context.Context) {
+				discovered, err := sm.discoverAndSetupStream(ctx)
 				if err != nil {
 					sm.logger.Err(err)
 				}
@@ -152,7 +152,7 @@ func (sm *streamManager) loop() {
 						sm.coolDown.UnSet()
 					}()
 				}
-			}()
+			}(discCtx)
 
 		case addStream := <-sm.addStreamCh:
 			err := sm.handleAddStream(addStream.st)
```
