# [?] eth/downloader: fixes data race between synchronize and other methods (#21201)

## Summary
Severity: Unknown
Chain: Celo
Component: celo-org/celo-blockchain
Published: 2020-06-30
Source: https://github.com/celo-org/celo-blockchain/commit/d671dbd5b79d2213b92c2c187b9016c4309881c9
Type: security-commit

## Details
eth/downloader: fixes data race between synchronize and other methods (#21201)

* eth/downloaded: fixed datarace between synchronize and Progress

There was a race condition between `downloader.synchronize()` and `Progress` `syncWithPeer` `fetchHeight` `findAncestors` and `processHeaders`
This PR changes the behavior of the downloader a bit.
Previously the functions `Progress` `syncWithPeer` `fetchHeight` `findAncestors` and `processHeaders` read the syncMode anew within their loops. Now they read the syncMode at the start of their function and don't change it during their runtime.

* eth/downloaded: comment

* eth/downloader: added comment

## Patch
### eth/downloader/downloader.go
```diff
@@ -100,7 +100,7 @@ type Downloader struct {
 	rttEstimate   uint64 // Round trip time to target for download requests
 	rttConfidence uint64 // Confidence in the estimated RTT (unit: millionths to allow atomic ops)
 
-	mode SyncMode       // Synchronisation mode defining the strategy used (per sync cycle)
+	mode uint32         // Synchronisation mode defining the strategy used (per sync cycle), use d.getMode() to get the SyncMode
 	mux  *event.TypeMux // Event multiplexer to announce sync operation events
 
 	checkpoint uint64   // Checkpoint block number to enforce head against (e.g. fast sync)
@@ -258,15 +258,16 @@ func (d *Downloader) Progress() ethereum.SyncProgress {
 	defer d.syncStatsLock.RUnlock()
 
 	current := uint64(0)
+	mode := d.getMode()
 	switch {
-	case d.blockchain != nil && d.mode == FullSync:
+	case d.blockchain != nil && mode == FullSync:
 		current = d.blockchain.CurrentBlock().NumberU64()
-	case d.blockchain != nil && d.mode == FastSync:
+	case d.blockchain != nil && mode == FastSync:
 		current = d.blockchain.CurrentFastBlock().NumberU64()
 	case d.lightchain != nil:
 		current = d.lightchain.CurrentHeader().Number.Uint64()
 	default:
-		log.Error("Unknown downloader chain/mode combo", "light", d.lightchain != nil, "full", d.blockchain != nil, "mode", d.mode)
+		log.Error("Unknown downloader chain/mode combo", "light", d.lightchain != nil, "full", d.blockchain != nil, "mode", mode)
 	}
 	return ethereum.SyncProgress{
 		StartingBlock: d.syncStatsChainOrigin,
@@ -415,8 +416,8 @@ func (d *Downloader) synchronise(id string, hash common.Hash, td *big.Int, mode
 
 	defer d.Cancel() // No matter what, we can't leave the cancel channel open
 
-	// Set the requested sync mode, unless it's forbidden
-	d.mode = mode
+	// Atomically set the requested sync mode
+	atomic.StoreUint32(&d.mode, uint32(mode))
 
 	// Retrieve the origin peer and initiate the downloading process
 	p := d.peers.Peer(id)
@@ -426,6 +427,10 @@ func (d *Downloader) synchronise(id string, hash common.Hash, td *big.Int, mode
 	return d.syncWithPeer(p, hash, td)
 }
 
+func (d *Downloader) getMode() SyncMode {
+	return SyncMode(atomic.LoadUint32(&d.mode))
+}
+
 // syncWithPeer starts a block synchronization based on the hash chain from the
 // specified peer and head hash.
 func (d *Downloader) syncWithPeer(p *peerConnection, hash common.Hash, td *big.Int) (err error) {
@@ -442,8 +447,9 @@ func (d *Downloader) syncWithPeer(p *peerConnection, hash common.Hash, td *big.I
 	if p.version < 62 {
 		return errTooOld
 	}
+	mode := d.getMode()
 
-	log.Debug("Synchronising with the network", "peer", p.id, "eth", p.version, "head", hash, "td", td, "mode", d.mode)
+	log.Debug("Synchronising with the network", "peer", p.id, "eth", p.version, "head", hash, "td", td, "mode", mode)
 	defer func(start time.Time) {
 		log.Debug("Synchronisation terminated", "elapsed", common.PrettyDuration(time.Since(start)))
 	}(time.Now())
@@ -468,7 +474,7 @@ func (d *Downloader) syncWithPeer(p *peerConnection, hash common.Hash, td *big.I
 
 	// Ensure our origin point is below any fast sync pivot point
 	pivot := uint64(0)
-	if d.mode == FastSync {
+	if mode == FastSync {
 		if height <= uint64(fsMinFullBlocks) {
 			origin = 0
 		} else {
@@ -479,10 +485,10 @@ func (d *Downloader) syncWithPeer(p *peerConnection, hash common.Hash, td *big.I
 		}
 	}
 	d.committed = 1
-	if d.mode == FastSync && pivot != 0 {
+	if mode == FastSync && pivot != 0 {
 		d.committed = 0
 	}
-	if d.mode == FastSync {
+	if mode == FastSync {
 		// Set the ancient data limitation.
 		// If we are running fast sync, all block data older than ancientLimit will be
 		// written to the ancient store. More recent data will be written to the active
@@ -521,7 +527,7 @@ func (d *Downloader) syncWithPeer(p *peerConnection, hash common.Hash, td *big.I
 		}
 	}
 	// Initiate the sync using a concurrent header and content retrieval algorithm
-	d.queue.Prepare(origin+1, d.mode)
+	d.queue.Prepare(origin+1, mode)
 	if d.syncInitHook != nil {
 		d.syncInitHook(origin, height)
 	}
@@ -531,9 +537,9 @@ func (d *Downloader) syncWithPeer(p *peerConnection, hash common.Hash, td *big.I
 		func() error { return d.fetchReceipts(origin + 1) },        // Receipts are retrieved during fast sync
 		func() error { return d.processHeaders(origin+1, pivot, td) },
 	}
-	if d.mode == FastSync {
+	if mode == FastSync {
 		fetchers = append(fetchers, func() error { return d.processFastSyncContent(latest) })
-	} else if d.mode == FullSync {
+	} else if mode == FullSync {
 		fetchers = append(fetchers, d.processFullSyncContent)
 	}
 	return d.spawnSync(fetchers)
@@ -621,6 +627,7 @@ func (d *Downloader) fetchHeight(p *peerConnection) (*types.Header, error) {
 
 	ttl := d.requestTTL()
 	timeout := time.After(ttl)
+	mode := d.getMode()
 	for {
 		select {
 		case <-d.cancelCh:
@@ -639,7 +646,7 @@ func (d *Downloader) fetchHeight(p *peerConnection) (*types.Header, error) {
 				return nil, errBadPeer
 			}
 			head := headers[0]
-			if (d.mode == FastSync || d.mode == LightSync) && head.Number.Uint64() < d.checkpoint {
+			if (mode == FastSync || mode == LightSync) && head.Number.Uint64() < d.checkpoint {
 				p.log.Warn("Remote head below checkpoint", "number", head.Number, "hash", head.Hash())
 				return nil, errUnsyncedPeer
 			}
@@ -721,7 +728,8 @@ func (d *Downloader) findAncestor(p *peerConnection, remoteHeader *types.Header)
 		localHeight  uint64
 		remoteHeight = remoteHeader.Number.Uint64()
 	)
-	switch d.mode {
+	mode := d.getMode()
+	switch mode {
 	case FullSync:
 		localHeight = d.blockchain.CurrentBlock().NumberU64()
 	case FastSync:
@@ -738,7 +746,7 @@ func (d *Downloader) findAncestor(p *peerConnection, remoteHeader *types.Header)
 	}
 	// If we're doing a light sync, ensure the floor doesn't go below the CHT, as
 	// all headers before that point will be missing.
-	if d.mode == LightSync {
+	if mode == LightSync {
 		// If we don't know the current CHT position, find it
 		if d.genesis == 0 {
 			header := d.lightchain.CurrentHeader()
@@ -804,7 +812,7 @@ func (d *Downloader) findAncestor(p *peerConnection, remoteHeader *types.Header)
 				n := headers[i].Number.Uint64()
 
 				var known bool
-				switch d.mode {
+				switch mode {
 				case FullSync:
 					known = d.blockchain.HasBlock(h, n)
 				case FastSync:
@@ -877,7 +885,7 @@ func (d *Downloader) findAncestor(p *peerConnection, remoteHeader *types.Header)
 				n := headers[0].Number.Uint64()
 
 				var known bool
-				switch d.mode {
+				switch mode {
 				case FullSync:
 					known = d.blockchain.HasBlock(h, n)
 				case FastSync:
@@ -954,6 +962,7 @@ func (d *Downloader) fetchHeaders(p *peerConnection, from uint64, pivot uint64)
 	ancestor := from
 	getHeaders(from)
 
+	mode := d.getMode()
 	for {
 		select {
 		case <-d.cancelCh:
@@ -1014,7 +1023,7 @@ func (d *Downloader) fetchHeaders(p *peerConnection, from uint64, pivot uint64)
 				if n := len(headers); n > 0 {
 					// Retrieve the current head we're at
 					var head uint64
-					if d.mode == LightSync {
+					if mode == LightSync {
 						head = d.lightchain.CurrentHeader().Number.Uint64()
 					} else {
 						head = d.blockchain.CurrentFastBlock().NumberU64()
@@ -1375,6 +1384,7 @@ func (d *Downloader) fetchParts(deliveryCh chan dataPack, deliver func(dataPack)
 func (d *Downloader) processHeaders(origin uint64, pivot uint64, td *big.Int) error {
 	// Keep a count of uncertain headers to roll back
 	var rollback []*types.Header
+	mode := d.getMode()
 	defer func() {
 		if len(rollback) > 0 {
 			// Flatten the headers and roll them back
@@ -1383,13 +1393,13 @@ func (d *Downloader) processHeaders(origin uint64, pivot uint64, td *big.Int) er
 				hashes[i] = header.Hash()
 			}
 			lastHeader, lastFastBlock, lastBlock := d.lightchain.CurrentHeader().Number, common.Big0, common.Big0
-			if d.mode != LightSync {
+			if mode != LightSync {
 				lastFastBlock = d.blockchain.CurrentFastBlock().Number()
 				lastBlock = d.blockchain.CurrentBlock().Number()
 			}
 			d.lightchain.Rollback(hashes)
 			curFastBlock, curBlock := common.Big0, common.Big0
-			if d.mode != LightSync {
+			if mode != LightSync {
 				curFastBlock = d.blockchain.CurrentFastBlock().Number()
 				curBlock = d.blockchain.CurrentBlock().Number()
 			}
@@ -1430,7 +1440,7 @@ func (d *Downloader) processHeaders(origin uint64, pivot uint64, td *big.Int) er
 				// L: Sync begins, and finds common ancestor at 11
 				// L: Request new headers up from 11 (R's TD was higher, it must have something)
 				// R: Nothing to give
-				if d.mode != LightSync {
+				if mode != LightSync {
 					head := d.blockchain.CurrentBlock()
 					if !gotHeaders && td.Cmp(d.blockchain.GetTd(head.Hash(), head.NumberU64())) > 0 {
 						return errStallingPeer
@@ -1443,7 +1453,7 @@ func (d *Downloader) processHeaders(origin uint64, pivot uint64, td *big.Int) er
 				// This check cannot be executed "as is" for full imports, since blocks may still be
 				// queued for processing when the header download completes. However, as long as the
 				// peer gave us something useful, we're already happy/progressed (above check).
-				if d.mode == FastSync || d.mode == LightSync {
+				if mode == FastSync || mode == LightSync {
 					head := d.lightchain.CurrentHeader()
 					if td.Cmp(d.lightchain.GetTd(head.Hash(), head.Number.Uint64())) > 0 {
 						return errStallingPeer
@@ -1469,7 +1479,7 @@ func (d *Downloader) processHeaders(origin uint64, pivot uint64, td *big.Int) er
 				}
 				chunk := headers[:limit]
 				// In case of header only syncing, validate the chunk immediately
-				if d.mode == FastSync || d.mode == LightSync {
+				if mode == FastSync || mode == LightSync {
 					// Collect the yet unknown headers to mark them as uncertain
 					unknown := make([]*types.Header, 0, len(chunk))
 					for _, header := range chunk {
@@ -1497,7 +1507,7 @@ func (d *Downloader) processHeaders(origin uint64, pivot uint64, td *big.Int) er
 					}
 				}
 				// Unless we're doing light chains, schedule the headers for associated content retrieval
-				if d.mode == FullSync || d.mode == FastSync {
+				if mode == FullSync || mode == FastSync {
 					// If we've reached the allowed number of pending headers, stall a bit
 					for d.queue.PendingBlocks() >= maxQueuedHeaders || d.queue.PendingReceipts() >= maxQueuedHeaders {
 						select {
```

### eth/downloader/downloader_test.go
```diff
@@ -483,7 +483,7 @@ func assertOwnForkedChain(t *testing.T, tester *downloadTester, common int, leng
 		blocks += length - common
 		receipts += length - common
 	}
-	if tester.downloader.mode == LightSync {
+	if tester.downloader.getMode() == LightSync {
 		blocks, receipts = 1, 1
 	}
 	if hs := len(tester.ownHeaders) + len(tester.ancientHeaders) - 1; hs != headers {
```

### eth/downloader/modes.go
```diff
@@ -19,7 +19,8 @@ package downloader
 import "fmt"
 
 // SyncMode represents the synchronisation mode of the downloader.
-type SyncMode int
+// It is a uint32 as it is used with atomic operations.
+type SyncMode uint32
 
 const (
 	FullSync  SyncMode = iota // Synchronise the entire blockchain history from full blocks
```
