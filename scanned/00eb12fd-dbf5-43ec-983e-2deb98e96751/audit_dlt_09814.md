# [?] [sync] fix a panic issue found in stream tests

## Summary
Severity: Unknown
Chain: Harmony
Component: harmony-one/harmony
Published: 2021-05-03
Source: https://github.com/harmony-one/harmony/commit/d8b5d1693a04754af162379c6ac82c25ec31b30c
Type: security-commit

## Details
[sync] fix a panic issue found in stream tests

## Patch
### node/node_syncing.go
```diff
@@ -87,8 +87,15 @@ func (node *Node) createStateSync() *legacysync.StateSync {
 	// Thus for compatibility, we are doing the arithmetics here, and not to change the
 	// protocol itself. This is just the temporary hack and will not be a concern after
 	// state sync.
-	syncPort := node.downloaderServer.Port
-	mutatedPort := strconv.Itoa(syncPort + legacysync.SyncingPortDifference)
+	var mySyncPort int
+	if node.downloaderServer != nil {
+		mySyncPort = node.downloaderServer.Port
+	} else {
+		// If local sync server is not started, the port field in protocol is actually not
+		// functional, simply set it to default value.
+		mySyncPort = nodeconfig.DefaultDNSPort
+	}
+	mutatedPort := strconv.Itoa(mySyncPort + legacysync.SyncingPortDifference)
 	return legacysync.CreateStateSync(node.SelfPeer.IP, mutatedPort,
 		node.GetSyncID(), node.NodeConfig.Role() == nodeconfig.ExplorerNode)
 }
```
