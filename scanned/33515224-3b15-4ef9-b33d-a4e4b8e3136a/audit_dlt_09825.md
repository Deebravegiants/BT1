# [?] [viewchange] avoid reentrant of newview message

## Summary
Severity: Unknown
Chain: Harmony
Component: harmony-one/harmony
Published: 2020-10-01
Source: https://github.com/harmony-one/harmony/commit/85f782f78308ad75f83a1c5426ad831d1b80aea7
Type: security-commit

## Details
[viewchange] avoid reentrant of newview message

Signed-off-by: Leo Chen <leo@harmony.one>

## Patch
### consensus/view_change.go
```diff
@@ -296,7 +296,7 @@ func (consensus *Consensus) onViewChange(msg *msg_pb.Message) {
 			}
 		}
 
-		consensus.SetViewChangingID(recvMsg.ViewID)
+		consensus.SetViewIDs(recvMsg.ViewID)
 		msgToSend := consensus.constructNewViewMessage(
 			recvMsg.ViewID, newLeaderPriKey,
 		)
@@ -316,7 +316,6 @@ func (consensus *Consensus) onViewChange(msg *msg_pb.Message) {
 			Hex("M1Payload", consensus.vc.GetM1Payload()).
 			Msg("[onViewChange] Sent NewView Messge")
 
-		consensus.SetCurBlockViewID(recvMsg.ViewID)
 		consensus.ResetViewChangeState()
 		consensus.consensusTimeout[timeoutViewChange].Stop()
 		consensus.consensusTimeout[timeoutConsensus].Start()
@@ -405,6 +404,11 @@ func (consensus *Consensus) onNewView(msg *msg_pb.Message) {
 		}
 	}
 
+	if !consensus.IsViewChangingMode() {
+		consensus.getLogger().Info().Msg("Not in ViewChanging Mode.")
+		return
+	}
+
 	// newView message verified success, override my state
 	consensus.SetViewIDs(recvMsg.ViewID)
 	consensus.LeaderPubKey = recvMsg.SenderPubkey
```
