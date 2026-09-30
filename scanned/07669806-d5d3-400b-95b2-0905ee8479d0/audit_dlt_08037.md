# [?] eth: fix sync bloom panic (#19757)

## Summary
Severity: Unknown
Chain: Celo
Component: celo-org/celo-blockchain
Published: 2019-06-26
Source: https://github.com/celo-org/celo-blockchain/commit/fd072c2fd1cfab5d8064985d21832fcac50045eb
Type: security-commit

## Details
eth: fix sync bloom panic (#19757)

* eth: fix sync bloom panic

* eth: delete useless test cases

## Patch
### eth/handler.go
```diff
@@ -121,9 +121,28 @@ func NewProtocolManager(config *params.ChainConfig, mode downloader.SyncMode, ne
 		txsyncCh:    make(chan *txsync),
 		quitSync:    make(chan struct{}),
 	}
-	// If fast sync was requested and our database is empty, grant it
-	if mode == downloader.FastSync && blockchain.CurrentBlock().NumberU64() == 0 {
-		manager.fastSync = uint32(1)
+	if mode == downloader.FullSync {
+		// The database seems empty as the current block is the genesis. Yet the fast
+		// block is ahead, so fast sync was enabled for this node at a certain point.
+		// The scenarios where this can happen is
+		// * if the user manually (or via a bad block) rolled back a fast sync node
+		//   below the sync point.
+		// * the last fast sync is not finished while user specifies a full sync this
+		//   time. But we don't have any recent state for full sync.
+		// In these cases however it's safe to reenable fast sync.
+		fullBlock, fastBlock := blockchain.CurrentBlock(), blockchain.CurrentFastBlock()
+		if fullBlock.NumberU64() == 0 && fastBlock.NumberU64() > 0 {
+			manager.fastSync = uint32(1)
+			log.Warn("Switch sync mode from full sync to fast sync")
+		}
+	} else {
+		if blockchain.CurrentBlock().NumberU64() > 0 {
+			// Print warning log if database is not empty to run fast sync.
+			log.Warn("Switch sync mode from fast sync to full sync")
+		} else {
+			// If fast sync was requested and our database is empty, grant it
+			manager.fastSync = uint32(1)
+		}
 	}
 	// If we have trusted checkpoints, enforce them on the chain
 	if checkpoint, ok := params.TrustedCheckpoints[blockchain.Genesis().Hash()]; ok {
```

### eth/handler_test.go
```diff
@@ -468,27 +468,22 @@ func TestCheckpointChallenge(t *testing.T) {
 		// If checkpointing is not enabled locally, don't challenge and don't drop
 		{downloader.FullSync, false, false, false, false, false},
 		{downloader.FastSync, false, false, false, false, false},
-		{downloader.LightSync, false, false, false, false, false},
 
 		// If checkpointing is enabled locally and remote response is empty, only drop during fast sync
 		{downloader.FullSync, true, false, true, false, false},
 		{downloader.FastSync, true, false, true, false, true}, // Special case, fast sync, unsynced peer
-		{downloader.LightSync, true, false, true, false, false},
 
 		// If checkpointing is enabled locally and remote response mismatches, always drop
 		{downloader.FullSync, true, false, false, false, true},
 		{downloader.FastSync, true, false, false, false, true},
-		{downloader.LightSync, true, false, false, false, true},
 
 		// If checkpointing is enabled locally and remote response matches, never drop
 		{downloader.FullSync, true, false, false, true, false},
 		{downloader.FastSync, true, false, false, true, false},
-		{downloader.LightSync, true, false, false, true, false},
 
 		// If checkpointing is enabled locally and remote times out, always drop
 		{downloader.FullSync, true, true, false, true, true},
 		{downloader.FastSync, true, true, false, true, true},
-		{downloader.LightSync, true, true, false, true, true},
 	}
 	for _, tt := range tests {
 		t.Run(fmt.Sprintf("sync %v checkpoint %v timeout %v empty %v match %v", tt.syncmode, tt.checkpoint, tt.timeout, tt.empty, tt.match), func(t *testing.T) {
```

### eth/sync.go
```diff
@@ -179,14 +179,6 @@ func (pm *ProtocolManager) synchronise(peer *peer) {
 	if atomic.LoadUint32(&pm.fastSync) == 1 {
 		// Fast sync was explicitly requested, and explicitly granted
 		mode = downloader.FastSync
-	} else if currentBlock.NumberU64() == 0 && pm.blockchain.CurrentFastBlock().NumberU64() > 0 {
-		// The database seems empty as the current block is the genesis. Yet the fast
-		// block is ahead, so fast sync was enabled for this node at a certain point.
-		// The only scenario where this can happen is if the user manually (or via a
-		// bad block) rolled back a fast sync node below the sync point. In this case
-		// however it's safe to reenable fast sync.
-		atomic.StoreUint32(&pm.fastSync, 1)
-		mode = downloader.FastSync
 	}
 	if mode == downloader.FastSync {
 		// Make sure the peer's total difficulty we are synchronizing is higher.
```
