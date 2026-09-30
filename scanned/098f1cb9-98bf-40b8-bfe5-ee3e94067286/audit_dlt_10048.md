# [?] add underflow protection

## Summary
Severity: Unknown
Chain: MultiversX
Component: multiversx/mx-chain-go
Published: 2026-02-06
Source: https://github.com/multiversx/mx-chain-go/commit/c06c709e19144db4295b7991451f35d5866fe8c9
Type: security-commit

## Details
add underflow protection

## Patch
### process/block/preprocess/blockSizeComputation.go
```diff
@@ -18,8 +18,8 @@ type blockSizeComputation struct {
 	miniblockSize uint32
 	txSize        uint32
 
-	numMiniBlocks      uint32
-	numTxs             uint32
+	numMiniBlocks      int32
+	numTxs             int32
 	blockSizeThrottler BlockSizeThrottler
 	maxSize            uint32
 }
@@ -120,35 +120,35 @@ func (bsc *blockSizeComputation) generateDummyMiniblock(numTxHashes int) *block.
 
 // Init reset the stored values of accumulated numTxs and numMiniBlocks
 func (bsc *blockSizeComputation) Init() {
-	atomic.StoreUint32(&bsc.numTxs, 0)
-	atomic.StoreUint32(&bsc.numMiniBlocks, 0)
+	atomic.StoreInt32(&bsc.numTxs, 0)
+	atomic.StoreInt32(&bsc.numMiniBlocks, 0)
 }
 
 // AddNumMiniBlocks adds the provided value to numMiniBlocks in a concurrent safe manner
 func (bsc *blockSizeComputation) AddNumMiniBlocks(numMiniBlocks int) {
-	atomic.AddUint32(&bsc.numMiniBlocks, uint32(numMiniBlocks))
+	atomic.AddInt32(&bsc.numMiniBlocks, int32(numMiniBlocks))
 }
 
 // DecNumMiniBlocks decrements the provided value to numMiniBlocks in a concurrent safe manner
 func (bsc *blockSizeComputation) DecNumMiniBlocks(numMiniBlocks int) {
-	atomic.AddUint32(&bsc.numMiniBlocks, ^uint32(numMiniBlocks-1))
+	atomic.AddInt32(&bsc.numMiniBlocks, -int32(numMiniBlocks))
 }
 
 // AddNumTxs adds the provided value to numTxs in a concurrent safe manner
 func (bsc *blockSizeComputation) AddNumTxs(numTxs int) {
-	atomic.AddUint32(&bsc.numTxs, uint32(numTxs))
+	atomic.AddInt32(&bsc.numTxs, int32(numTxs))
 }
 
 // DecNumTxs decrements the provided value to numTxs in a concurrent safe manner
 func (bsc *blockSizeComputation) DecNumTxs(numTxs int) {
-	atomic.AddUint32(&bsc.numTxs, ^uint32(numTxs-1))
+	atomic.AddInt32(&bsc.numTxs, -int32(numTxs))
 }
 
 // IsMaxBlockSizeReached returns true if the provided number of new miniblocks and txs go over
 // the maximum allowed throttled block size
 func (bsc *blockSizeComputation) IsMaxBlockSizeReached(numNewMiniBlocks int, numNewTxs int) bool {
-	totalMiniBlocks := atomic.LoadUint32(&bsc.numMiniBlocks) + uint32(numNewMiniBlocks)
-	totalTxs := atomic.LoadUint32(&bsc.numTxs) + uint32(numNewTxs)
+	totalMiniBlocks := uint32(atomic.LoadInt32(&bsc.numMiniBlocks)) + uint32(numNewMiniBlocks)
+	totalTxs := uint32(atomic.LoadInt32(&bsc.numTxs)) + uint32(numNewTxs)
 
 	return bsc.isMaxBlockSizeReached(totalMiniBlocks, totalTxs)
 }
@@ -166,8 +166,8 @@ func (bsc *blockSizeComputation) isMaxBlockSizeReached(
 // IsMaxBlockSizeWithoutThrottleReached returns true if the provided number of new miniblocks and txs go over
 // the maximum allowed not throttled block size
 func (bsc *blockSizeComputation) IsMaxBlockSizeWithoutThrottleReached(numNewMiniBlocks int, numNewTxs int) bool {
-	totalMiniBlocks := atomic.LoadUint32(&bsc.numMiniBlocks) + uint32(numNewMiniBlocks)
-	totalTxs := atomic.LoadUint32(&bsc.numTxs) + uint32(numNewTxs)
+	totalMiniBlocks := uint32(atomic.LoadInt32(&bsc.numMiniBlocks)) + uint32(numNewMiniBlocks)
+	totalTxs := uint32(atomic.LoadInt32(&bsc.numTxs)) + uint32(numNewTxs)
 
 	return bsc.isMaxBlockSizeWithoutThrottleReached(totalMiniBlocks, totalTxs)
 }
```

### process/block/preprocess/export_test.go
```diff
@@ -110,12 +110,12 @@ func (bsc *blockSizeComputation) TxSize() uint32 {
 
 // NumMiniBlocks -
 func (bsc *blockSizeComputation) NumMiniBlocks() uint32 {
-	return atomic.LoadUint32(&bsc.numMiniBlocks)
+	return uint32(atomic.LoadInt32(&bsc.numMiniBlocks))
 }
 
 // NumTxs -
 func (bsc *blockSizeComputation) NumTxs() uint32 {
-	return atomic.LoadUint32(&bsc.numTxs)
+	return uint32(atomic.LoadInt32(&bsc.numTxs))
 }
 
 // ProcessTxsToMe -
```
