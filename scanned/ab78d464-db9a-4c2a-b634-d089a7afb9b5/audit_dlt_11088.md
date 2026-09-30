# [?] fix possible panic in computeSyncActions (#13287)

## Summary
Severity: Unknown
Chain: Boba
Component: bobanetwork/boba
Published: 2024-12-06
Source: https://github.com/bobanetwork/boba/commit/0c9b1d5268827044c5be409645ed52dad56d47f6
Type: security-commit

## Details
fix possible panic in computeSyncActions (#13287)

## Patch
### op-batcher/batcher/sync_actions.go
```diff
@@ -114,7 +114,7 @@ func computeSyncActions[T channelStatuser](newSyncStatus eth.SyncStatus, prevCur
 			// that the derivation pipeline may have stalled
 			// e.g. because of Holocene strict ordering rules.
 			l.Warn("sequencer did not make expected progress",
-				"existingBlock", eth.ToBlockID(blocks[numBlocksToDequeue-1]),
+				"existingBlock", ch.LatestL2(),
 				"newSafeBlock", newSyncStatus.SafeL2,
 				"syncActions", startAfresh)
 			return startAfresh, false
```
