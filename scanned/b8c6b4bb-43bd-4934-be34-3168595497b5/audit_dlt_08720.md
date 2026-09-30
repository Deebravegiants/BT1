# [?] Fix deadlock caused by txStreamer trying to broadcast an executed message during a stopAndWait

## Summary
Severity: Unknown
Chain: Arbitrum
Component: OffchainLabs/nitro
Published: 2025-03-04
Source: https://github.com/OffchainLabs/nitro/commit/14787f87de45cbde26547b4a4919f22223d57359
Type: security-commit

## Details
Fix deadlock caused by txStreamer trying to broadcast an executed message during a stopAndWait

## Patch
### wsbroadcastserver/clientmanager.go
```diff
@@ -142,13 +142,17 @@ func (cm *ClientManager) ClientCount() int32 {
 
 // Broadcast sends batch item to all clients.
 func (cm *ClientManager) Broadcast(bm *m.BroadcastMessage) {
-	if cm.Stopped() {
+	ctx, err := cm.GetContextSafe()
+	if err != nil {
+		return
+	}
+	select {
+	case cm.broadcastChan <- bm:
+	case <-ctx.Done():
 		// This should only occur if a reorg occurs after the broadcast server is stopped,
 		// with the sequencer enabled but not the sequencer coordinator.
 		// In this case we should proceed without broadcasting the message.
-		return
 	}
-	cm.broadcastChan <- bm
 }
 
 func (cm *ClientManager) doBroadcast(bm *m.BroadcastMessage) ([]*ClientConnection, error) {
```
