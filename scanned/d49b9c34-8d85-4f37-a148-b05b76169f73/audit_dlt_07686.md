# [?] Caplin: fixed remote DOS (#13482)

## Summary
Severity: Unknown
Chain: Ethereum
Component: erigontech/erigon
Published: 2025-01-19
Source: https://github.com/erigontech/erigon/commit/37cf19f94f7983bd7b349f106633bdaff3bdd815
Type: security-commit

## Details
Caplin: fixed remote DOS (#13482)

added circuit breaker if too many iterations are performed

## Patch
### cl/sentinel/handlers/blobs.go
```diff
@@ -51,7 +51,13 @@ func (c *ConsensusHandlers) blobsSidecarsByRangeHandler(s network.Stream, versio
 	defer tx.Rollback()
 
 	written := 0
+	maxIter := 32
+	currIter := 0
 	for slot := req.StartSlot; slot < req.StartSlot+req.Count; slot++ {
+		if currIter >= maxIter {
+			break
+		}
+		currIter++
 		blockRoot, err := beacon_indicies.ReadCanonicalBlockRoot(tx, slot)
 		if err != nil {
 			return err
```
