# [?] fix(gossip): prevent panic on state provider shutdown (#5378)

## Summary
Severity: Unknown
Chain: Hyperledger Fabric
Component: hyperledger/fabric
Published: 2026-01-27
Source: https://github.com/hyperledger/fabric/commit/d6d621f63dfbf6a9ce4ac527e934189275bc25e3
Type: security-commit

## Details
fix(gossip): prevent panic on state provider shutdown (#5378)

Signed-off-by: Ady0333 <adityashinde1525@gmail.com>

## Patch
### gossip/state/state.go
```diff
@@ -389,16 +389,17 @@ func (s *GossipStateProviderImpl) directMessage(msg protoext.ReceivedMessage) {
 
 	if incoming.GetStateRequest() != nil {
 		if len(s.stateRequestCh) < s.config.StateChannelSize {
-			// Forward state request to the channel, if there are too
-			// many message of state request ignore to avoid flooding.
-			s.stateRequestCh <- msg
+			select {
+			case s.stateRequestCh <- msg:
+			case <-s.stopCh:
+			}
 		}
 	} else if incoming.GetStateResponse() != nil {
-		// If no state transfer procedure activate there is
-		// no reason to process the message
 		if atomic.LoadInt32(&s.stateTransferActive) == 1 {
-			// Send signal of state response message
-			s.stateResponseCh <- msg
+			select {
+			case s.stateResponseCh <- msg:
+			case <-s.stopCh:
+			}
 		}
 	}
 }
```
