# [?] resolved race condition

## Summary
Severity: Unknown
Chain: Celo
Component: celo-org/celo-blockchain
Published: 2020-02-10
Source: https://github.com/celo-org/celo-blockchain/commit/d574a3722f3b506d14e6ade91cb23bb1393b41fe
Type: security-commit

## Details
resolved race condition

## Patch
### consensus/istanbul/backend/announce.go
```diff
@@ -203,7 +203,7 @@ func (sb *Backend) pruneAnnounceDataStructures() error {
 			delete(sb.cachedAnnounceMsgs, cachedValAddress)
 		}
 	}
-	defer sb.cachedAnnounceMsgsMu.Unlock()
+	sb.cachedAnnounceMsgsMu.Unlock()
 
 	sb.lastAnnounceGossipedMu.Lock()
 	for remoteAddress := range sb.lastAnnounceGossiped {
@@ -212,7 +212,7 @@ func (sb *Backend) pruneAnnounceDataStructures() error {
 			delete(sb.lastAnnounceGossiped, remoteAddress)
 		}
 	}
-	defer sb.lastAnnounceGossipedMu.Unlock()
+	sb.lastAnnounceGossipedMu.Unlock()
 
 	if err := sb.valEnodeTable.PruneEntries(regAndElectedVals); err != nil {
 		logger.Trace("Error in pruning valEnodeTable", "err", err)
@@ -675,7 +675,7 @@ func (sb *Backend) handleAnnounceVersionsMsg(peer consensus.Peer, payload []byte
 		if cachedEntry, ok := sb.cachedAnnounceMsgs[announceVersion.ValAddress]; !ok || cachedEntry.MsgVersion < announceVersion.AnnounceMsgVersion {
 			announcesToRequest = append(announcesToRequest, announceVersion.ValAddress)
 		}
-		defer sb.cachedAnnounceMsgsMu.RUnlock()
+		sb.cachedAnnounceMsgsMu.RUnlock()
 	}
 
 	if len(announcesToRequest) > 0 {
```
