# [?] [sync] fix testnet syncing panic issue (#3308)

## Summary
Severity: Unknown
Chain: Harmony
Component: harmony-one/harmony
Published: 2020-08-21
Source: https://github.com/harmony-one/harmony/commit/bf86767e60e2ae8c89baf4b616c62ff4e74cf15e
Type: security-commit

## Details
[sync] fix testnet syncing panic issue (#3308)

* [sync] fix testnet syncing panic issue

* [sync] add back close connections in initialization

## Patch
### api/service/syncing/syncing.go
```diff
@@ -102,6 +102,7 @@ func CreateStateSync(ip string, port string, peerHash [20]byte) *StateSync {
 	stateSync.selfPeerHash = peerHash
 	stateSync.commonBlocks = make(map[int]*types.Block)
 	stateSync.lastMileBlocks = []*types.Block{}
+	stateSync.syncConfig = &SyncConfig{}
 	return stateSync
 }
 
```
