# [?] Fix panic message to mention right version of istanbul

## Summary
Severity: Unknown
Chain: Celo
Component: celo-org/celo-blockchain
Published: 2020-11-05
Source: https://github.com/celo-org/celo-blockchain/commit/b044f3c64cd69b49a212b9a5fe943318c4c29fed
Type: security-commit

## Details
Fix panic message to mention right version of istanbul

## Patch
### eth/sync.go
```diff
@@ -92,7 +92,7 @@ func (pm *ProtocolManager) txsyncLoop64() {
 	// send starts a sending a pack of transactions from the sync.
 	send := func(s *txsync) {
 		if s.p.version >= istanbul.Celo66 {
-			panic("initial transaction syncer running on eth/65+ (celo/65+)")
+			panic("initial transaction syncer running on eth/65+ (celo/66+)")
 		}
 		// Fill pack with transactions up to the target size.
 		size := common.StorageSize(0)
```
