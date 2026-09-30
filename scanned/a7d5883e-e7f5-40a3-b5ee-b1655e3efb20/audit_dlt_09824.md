# [?] avoid race condition

## Summary
Severity: Unknown
Chain: Harmony
Component: harmony-one/harmony
Published: 2020-10-26
Source: https://github.com/harmony-one/harmony/commit/8d72c537f12f5848961589bd966f53b4769ccb9e
Type: security-commit

## Details
avoid race condition

## Patch
### consensus/consensus_service.go
```diff
@@ -554,6 +554,9 @@ func (consensus *Consensus) selfCommit(payload []byte) error {
 	consensus.mutex.Lock()
 	defer consensus.mutex.Unlock()
 
+	// Have to keep the block hash so the leader can finish the commit phase of prepared block
+	consensus.ResetState()
+
 	copy(consensus.blockHash[:], blockHash[:])
 	consensus.switchPhase("selfCommit", FBFTCommit)
 	consensus.aggregatedPrepareSig = aggSig
```

### consensus/view_change.go
```diff
@@ -274,7 +274,7 @@ func (consensus *Consensus) startViewChange() {
 }
 
 // startNewView stops the current view change
-func (consensus *Consensus) startNewView(viewID uint64, newLeaderPriKey *bls.PrivateKeyWrapper) error {
+func (consensus *Consensus) startNewView(viewID uint64, newLeaderPriKey *bls.PrivateKeyWrapper, reset bool) error {
 	consensus.mutex.Lock()
 	defer consensus.mutex.Unlock()
 
@@ -317,7 +317,9 @@ func (consensus *Consensus) startNewView(viewID uint64, newLeaderPriKey *bls.Pri
 		Msg("[startNewView] viewChange stopped. I am the New Leader")
 
 	// TODO: consider make ResetState unified and only called in one place like finalizeCommit()
-	consensus.ResetState()
+	if reset {
+		consensus.ResetState()
+	}
 	consensus.LeaderPubKey = newLeaderPriKey.Pub
 
 	return nil
@@ -389,7 +391,7 @@ func (consensus *Consensus) onViewChange(msg *msg_pb.Message) {
 		// no previous prepared message, go straight to normal mode
 		// and start proposing new block
 		if consensus.vc.IsM1PayloadEmpty() {
-			if err := consensus.startNewView(recvMsg.ViewID, newLeaderPriKey); err != nil {
+			if err := consensus.startNewView(recvMsg.ViewID, newLeaderPriKey, true); err != nil {
 				consensus.getLogger().Error().Err(err).Msg("[onViewChange] startNewView failed")
 				return
 			}
@@ -405,12 +407,10 @@ func (consensus *Consensus) onViewChange(msg *msg_pb.Message) {
 			consensus.getLogger().Error().Err(err).Msg("[onViewChange] self commit failed")
 			return
 		}
-		if err := consensus.startNewView(recvMsg.ViewID, newLeaderPriKey); err != nil {
+		if err := consensus.startNewView(recvMsg.ViewID, newLeaderPriKey, false); err != nil {
 			consensus.getLogger().Error().Err(err).Msg("[onViewChange] startNewView failed")
 			return
 		}
-		// Have to keep the block hash so the leader can finish the commit phase of prepared block
-		copy(consensus.blockHash[:], payload[:32])
 	}
 }
 
```
