# [?] Fix panic. (#4440)

## Summary
Severity: Unknown
Chain: Harmony
Component: harmony-one/harmony
Published: 2023-06-06
Source: https://github.com/harmony-one/harmony/commit/6a2f9cd4c7f9a32a60cf3d9dcd5c76f393913425
Type: security-commit

## Details
Fix panic. (#4440)

* Fix panic.

* check for empty blockBytes in stage bodies

---------

Co-authored-by: “GheisMohammadi” <36589218+GheisMohammadi@users.noreply.github.com>

## Patch
### api/service/stagedstreamsync/block_manager.go
```diff
@@ -84,7 +84,7 @@ func (gbm *blockDownloadManager) HandleRequestResult(bns []uint64, blockBytes []
 
 	for i, bn := range bns {
 		delete(gbm.requesting, bn)
-		if len(blockBytes[i]) <= 1 {
+		if indexExists(blockBytes, i) && len(blockBytes[i]) <= 1 {
 			gbm.retries.push(bn)
 		} else {
 			gbm.processing[bn] = struct{}{}
@@ -97,6 +97,10 @@ func (gbm *blockDownloadManager) HandleRequestResult(bns []uint64, blockBytes []
 	return nil
 }
 
+func indexExists[T any](slice []T, index int) bool {
+	return index >= 0 && index < len(slice)
+}
+
 // SetDownloadDetails sets the download details for a batch of blocks
 func (gbm *blockDownloadManager) SetDownloadDetails(bns []uint64, loopID int, streamID sttypes.StreamID) error {
 	gbm.lock.Lock()
```

### api/service/stagedstreamsync/stage_bodies.go
```diff
@@ -168,6 +168,13 @@ func (b *StageBodies) runBlockWorkerLoop(gbm *blockDownloadManager, wg *sync.Wai
 				Msg(WrapStagedSyncMsg("downloadRawBlocks failed"))
 			err = errors.Wrap(err, "request error")
 			gbm.HandleRequestError(batch, err, stid)
+		} else if blockBytes == nil || len(blockBytes) == 0 {
+			utils.Logger().Warn().
+				Str("stream", string(stid)).
+				Interface("block numbers", batch).
+				Msg(WrapStagedSyncMsg("downloadRawBlocks failed, received empty blockBytes"))
+			err := errors.New("downloadRawBlocks received empty blockBytes")
+			gbm.HandleRequestError(batch, err, stid)
 		} else {
 			if err = b.saveBlocks(gbm.tx, batch, blockBytes, sigBytes, loopID, stid); err != nil {
 				panic(ErrSaveBlocksToDbFailed)
```
