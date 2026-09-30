# [?] Fix node panicing during shutdown. (#2043)

## Summary
Severity: Unknown
Chain: Algorand
Component: algorand/go-algorand
Published: 2021-04-06
Source: https://github.com/algorand/go-algorand/commit/356df58e7d996ef7ea4c2a6e35637be65e2ba809
Type: security-commit

## Details
Fix node panicing during shutdown. (#2043)

Fix node panicing during shutdown due to unsynchronized compactcert database access.

## Patch
### node/node.go
```diff
@@ -410,6 +410,10 @@ func (node *AlgorandFullNode) Stop() {
 	defer func() {
 		node.mu.Unlock()
 		node.waitMonitoringRoutines()
+		// we want to shut down the compactCert last, since the oldKeyDeletionThread might depend on it when making the
+		// call to LatestSigsFromThisNode.
+		node.compactCert.Shutdown()
+		node.compactCert = nil
 	}()
 
 	node.net.ClearHandlers()
@@ -429,7 +433,6 @@ func (node *AlgorandFullNode) Stop() {
 	node.lowPriorityCryptoVerificationPool.Shutdown()
 	node.cryptoPool.Shutdown()
 	node.cancelCtx()
-	node.compactCert.Shutdown()
 	if node.indexer != nil {
 		node.indexer.Shutdown()
 	}
```
