# [?] [sync] fix #3547 runtime panic in sync module

## Summary
Severity: Unknown
Chain: Harmony
Component: harmony-one/harmony
Published: 2021-02-24
Source: https://github.com/harmony-one/harmony/commit/72ae4da105877100c130e234ccb044d561a1e002
Type: security-commit

## Details
[sync] fix #3547 runtime panic in sync module

## Patch
### api/service/syncing/syncing.go
```diff
@@ -447,7 +447,7 @@ func (sc *SyncConfig) cleanUpPeers(maxFirstID int) {
 // Note that choosing the most common peer config does not guarantee that the blocks to be downloaded are the correct ones.
 // The subsequent node syncing steps of verifying the block header chain will give such confirmation later.
 // If later block header verification fails with the sync peer config chosen here, the entire sync loop gets retried with a new peer set.
-func (sc *SyncConfig) GetBlockHashesConsensusAndCleanUp() {
+func (sc *SyncConfig) GetBlockHashesConsensusAndCleanUp() error {
 	sc.mtx.Lock()
 	defer sc.mtx.Unlock()
 	// Sort all peers by the blockHashes.
@@ -459,11 +459,16 @@ func (sc *SyncConfig) GetBlockHashesConsensusAndCleanUp() {
 		Int("maxFirstID", maxFirstID).
 		Int("maxCount", maxCount).
 		Msg("[SYNC] block consensus hashes")
+
+	if maxFirstID == -1 {
+		return errors.New("invalid peer index -1 for block hashes query")
+	}
 	sc.cleanUpPeers(maxFirstID)
+	return nil
 }
 
 // getConsensusHashes gets all hashes needed to download.
-func (ss *StateSync) getConsensusHashes(startHash []byte, size uint32) {
+func (ss *StateSync) getConsensusHashes(startHash []byte, size uint32) error {
 	var wg sync.WaitGroup
 	ss.syncConfig.ForEachPeer(func(peerConfig *SyncPeerConfig) (brk bool) {
 		wg.Add(1)
@@ -492,8 +497,11 @@ func (ss *StateSync) getConsensusHashes(startHash []byte, size uint32) {
 		return
 	})
 	wg.Wait()
-	ss.syncConfig.GetBlockHashesConsensusAndCleanUp()
+	if err := ss.syncConfig.GetBlockHashesConsensusAndCleanUp(); err != nil {
+		return err
+	}
 	utils.Logger().Info().Msg("[SYNC] Finished getting consensus block hashes")
+	return nil
 }
 
 func (ss *StateSync) generateStateSyncTaskQueue(bc *core.BlockChain) {
@@ -860,7 +868,9 @@ func (ss *StateSync) generateNewState(bc *core.BlockChain, worker *worker.Worker
 // ProcessStateSync processes state sync from the blocks received but not yet processed so far
 func (ss *StateSync) ProcessStateSync(startHash []byte, size uint32, bc *core.BlockChain, worker *worker.Worker) error {
 	// Gets consensus hashes.
-	ss.getConsensusHashes(startHash, size)
+	if err := ss.getConsensusHashes(startHash, size); err != nil {
+		return errors.Wrap(err, "getConsensusHashes")
+	}
 	ss.generateStateSyncTaskQueue(bc)
 	// Download blocks.
 	if ss.stateSyncTaskQueue.Len() > 0 {
```
