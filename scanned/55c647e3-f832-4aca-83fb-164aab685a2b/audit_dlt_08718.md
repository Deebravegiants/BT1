# [?] Merge pull request #2991 from OffchainLabs/fix-stopandwait-deadlock

## Summary
Severity: Unknown
Chain: Arbitrum
Component: OffchainLabs/nitro
Published: 2025-03-10
Source: https://github.com/OffchainLabs/nitro/commit/7d9e31deb3166e2e5e93b4a2261543af9a74afb0
Type: security-commit

## Details
Merge pull request #2991 from OffchainLabs/fix-stopandwait-deadlock

Fix deadlock caused by txStreamer trying to broadcast an executed message during a stopAndWait

## Patch
### arbnode/node.go
```diff
@@ -1453,9 +1453,6 @@ func (n *Node) StopAndWait() {
 	if n.MessagePruner != nil && n.MessagePruner.Started() {
 		n.MessagePruner.StopAndWait()
 	}
-	if n.BroadcastServer != nil && n.BroadcastServer.Started() {
-		n.BroadcastServer.StopAndWait()
-	}
 	if n.BroadcastClients != nil {
 		n.BroadcastClients.StopAndWait()
 	}
@@ -1477,6 +1474,11 @@ func (n *Node) StopAndWait() {
 	if n.TxStreamer.Started() {
 		n.TxStreamer.StopAndWait()
 	}
+	// n.BroadcastServer is stopped after txStreamer and inboxReader because if done before it would lead to a deadlock, as the threads from these two components
+	// attempt to Broadcast i.e send feedMessage to clientManager's broadcastChan when there wont be any reader to read it as n.BroadcastServer would've been stopped
+	if n.BroadcastServer != nil && n.BroadcastServer.Started() {
+		n.BroadcastServer.StopAndWait()
+	}
 	if n.SeqCoordinator != nil && n.SeqCoordinator.Started() {
 		// Just stops the redis client (most other stuff was stopped earlier)
 		n.SeqCoordinator.StopAndWait()
```
