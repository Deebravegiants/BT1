# [?] fix race condition

## Summary
Severity: Unknown
Chain: Polygon CDK
Component: 0xPolygon/cdk
Published: 2024-07-15
Source: https://github.com/0xPolygon/cdk/commit/c9bd26b4f9b02450abe4f647a1739214a49d8f03
Type: security-commit

## Details
fix race condition

## Patch
### localbridgesync/downloader.go
```diff
@@ -38,18 +38,21 @@ type downloaderInterface interface {
 	getLogs(ctx context.Context, fromBlock, toBlock uint64) []types.Log
 	appendLog(b *block, l types.Log)
 	getBlockHeader(ctx context.Context, blockNum uint64) blockHeader
+	syncBlockChunkSize() uint64
 }
 
 type downloader struct {
 	bridgeAddr       common.Address
 	bridgeContractV1 *polygonzkevmbridge.Polygonzkevmbridge
 	bridgeContractV2 *polygonzkevmbridgev2.Polygonzkevmbridgev2
 	ethClient        EthClienter
+	blockChunkSize   uint64
 }
 
 func newDownloader(
 	bridgeAddr common.Address,
 	ethClient EthClienter,
+	syncBlockChunkSize uint64,
 ) (*downloader, error) {
 	bridgeContractV1, err := polygonzkevmbridge.NewPolygonzkevmbridge(bridgeAddr, ethClient)
 	if err != nil {
@@ -64,10 +67,11 @@ func newDownloader(
 		bridgeContractV1: bridgeContractV1,
 		bridgeContractV2: bridgeContractV2,
 		ethClient:        ethClient,
+		blockChunkSize:   syncBlockChunkSize,
 	}, nil
 }
 
-func download(ctx context.Context, d downloaderInterface, fromBlock, syncBlockChunkSize uint64, downloadedCh chan block) {
+func download(ctx context.Context, d downloaderInterface, fromBlock uint64, downloadedCh chan block) {
 	lastBlock := d.waitForNewBlocks(ctx, 0)
 	for {
 		select {
@@ -77,7 +81,7 @@ func download(ctx context.Context, d downloaderInterface, fromBlock, syncBlockCh
 			return
 		default:
 		}
-		toBlock := fromBlock + syncBlockChunkSize
+		toBlock := fromBlock + d.syncBlockChunkSize()
 		if toBlock > lastBlock {
 			toBlock = lastBlock
 		}
@@ -237,3 +241,7 @@ func (d *downloader) getBlockHeader(ctx context.Context, blockNum uint64) blockH
 		}
 	}
 }
+
+func (d *downloader) syncBlockChunkSize() uint64 {
+	return d.blockChunkSize
+}
```

### localbridgesync/downloader_test.go
```diff
@@ -24,7 +24,7 @@ var (
 )
 
 const (
-	syncBlockChunck = 10
+	syncBlockChunck = uint64(10)
 )
 
 func TestGetEventsByBlockRange(t *testing.T) {
@@ -37,7 +37,7 @@ func TestGetEventsByBlockRange(t *testing.T) {
 	testCases := []testCase{}
 	clientMock := NewL2Mock(t)
 	ctx := context.Background()
-	d, err := newDownloader(contractAddr, clientMock)
+	d, err := newDownloader(contractAddr, clientMock, syncBlockChunck)
 	require.NoError(t, err)
 
 	// case 0: single block, no events
@@ -278,6 +278,7 @@ func TestDownload(t *testing.T) {
 
 	d.On("waitForNewBlocks", mock.Anything, uint64(0)).
 		Return(uint64(1))
+	d.On("syncBlockChunkSize").Return(syncBlockChunck)
 	// iteratiion 0:
 	// last block is 1, download that block (no events and wait)
 	b1 := block{
@@ -390,7 +391,7 @@ func TestDownload(t *testing.T) {
 		After(time.Millisecond * 100).
 		Return(uint64(35)).Once()
 
-	go download(ctx1, d, 0, syncBlockChunck, downloadCh)
+	go download(ctx1, d, 0, downloadCh)
 	for _, expectedBlock := range expectedBlocks {
 		actualBlock := <-downloadCh
 		log.Debugf("block %d received!", actualBlock.Num)
@@ -406,7 +407,7 @@ func TestWaitForNewBlocks(t *testing.T) {
 	retryAfterErrorPeriod = time.Millisecond * 100
 	clientMock := NewL2Mock(t)
 	ctx := context.Background()
-	d, err := newDownloader(contractAddr, clientMock)
+	d, err := newDownloader(contractAddr, clientMock, syncBlockChunck)
 	require.NoError(t, err)
 
 	// at first attempt
@@ -433,7 +434,7 @@ func TestGetBlockHeader(t *testing.T) {
 	retryAfterErrorPeriod = time.Millisecond * 100
 	clientMock := NewL2Mock(t)
 	ctx := context.Background()
-	d, err := newDownloader(contractAddr, clientMock)
+	d, err := newDownloader(contractAddr, clientMock, syncBlockChunck)
 	require.NoError(t, err)
 
 	blockNum := uint64(5)
```

### localbridgesync/driver.go
```diff
@@ -14,7 +14,7 @@ const (
 )
 
 type driver struct {
-	reorgDetector ReorgDetectorInterface
+	reorgDetector ReorgDetector
 	reorgSub      *reorgdetector.Subscription
 	processor     processorInterface
 	downloader    downloaderInterface
@@ -26,15 +26,15 @@ type processorInterface interface {
 	reorg(firstReorgedBlock uint64) error
 }
 
-type ReorgDetectorInterface interface {
+type ReorgDetector interface {
 	Subscribe(id string) *reorgdetector.Subscription
 	AddBlockToTrack(ctx context.Context, id string, blockNum uint64, blockHash common.Hash) error
 }
 
-type downloadFn func(ctx context.Context, d downloaderInterface, fromBlock, syncBlockChunkSize uint64, downloadedCh chan block)
+type downloadFn func(ctx context.Context, d downloaderInterface, fromBlock uint64, downloadedCh chan block)
 
 func newDriver(
-	reorgDetector ReorgDetectorInterface,
+	reorgDetector ReorgDetector,
 	processor processorInterface,
 	downloader downloaderInterface,
 ) (*driver, error) {
@@ -47,7 +47,7 @@ func newDriver(
 	}, nil
 }
 
-func (d *driver) Sync(ctx context.Context, syncBlockChunkSize uint64, download downloadFn) {
+func (d *driver) Sync(ctx context.Context, download downloadFn) {
 reset:
 	var (
 		lastProcessedBlock uint64
@@ -69,7 +69,7 @@ reset:
 
 	// start downloading
 	downloadCh := make(chan block, downloadBufferSize)
-	go download(cancellableCtx, d.downloader, lastProcessedBlock, syncBlockChunkSize, downloadCh)
+	go download(cancellableCtx, d.downloader, lastProcessedBlock, downloadCh)
 
 	for {
 		select {
```

### localbridgesync/driver_test.go
```diff
@@ -3,6 +3,7 @@ package localbridgesync
 import (
 	"context"
 	"errors"
+	"sync"
 	"testing"
 	"time"
 
@@ -38,12 +39,16 @@ func TestSync(t *testing.T) {
 			Hash: common.HexToHash("09"),
 		},
 	}
-	reorg1Completed := false
+	type reorgSemaphore struct {
+		mu    sync.Mutex
+		green bool
+	}
+	reorg1Completed := reorgSemaphore{}
 
 	mockDownload := func(
 		ctx context.Context,
 		d downloaderInterface,
-		fromBlock, syncBlockChunkSize uint64,
+		fromBlock uint64,
 		downloadedCh chan block,
 	) {
 		log.Info("entering mock loop")
@@ -55,7 +60,10 @@ func TestSync(t *testing.T) {
 				return
 			default:
 			}
-			if reorg1Completed {
+			reorg1Completed.mu.Lock()
+			green := reorg1Completed.green
+			reorg1Completed.mu.Unlock()
+			if green {
 				downloadedCh <- expectedBlock2
 			} else {
 				downloadedCh <- expectedBlock1
@@ -75,7 +83,7 @@ func TestSync(t *testing.T) {
 		Return(nil)
 	pm.On("storeBridgeEvents", expectedBlock2.Num, expectedBlock2.Events).
 		Return(nil)
-	go driver.Sync(ctx, syncBlockChunck, mockDownload)
+	go driver.Sync(ctx, mockDownload)
 	time.Sleep(time.Millisecond * 200) // time to download expectedBlock1
 
 	// Trigger reorg 1
@@ -84,7 +92,9 @@ func TestSync(t *testing.T) {
 	firstReorgedBlock <- reorgedBlock1
 	ok := <-reorgProcessed
 	require.True(t, ok)
-	reorg1Completed = true
+	reorg1Completed.mu.Lock()
+	reorg1Completed.green = true
+	reorg1Completed.mu.Unlock()
 	time.Sleep(time.Millisecond * 200) // time to download expectedBlock2
 
 	// Trigger reorg 2: syncer restarts the porcess
```

### localbridgesync/localbridgesync.go
```diff
@@ -20,14 +20,15 @@ type LocalBridgeSync struct {
 func New(
 	dbPath string,
 	bridge common.Address,
-	rd ReorgDetectorInterface,
+	syncBlockChunkSize uint64,
+	rd ReorgDetector,
 	l2Client EthClienter,
 ) (*LocalBridgeSync, error) {
 	p, err := newProcessor(dbPath)
 	if err != nil {
 		return nil, err
 	}
-	dwn, err := newDownloader(bridge, l2Client)
+	dwn, err := newDownloader(bridge, l2Client, syncBlockChunkSize)
 	if err != nil {
 		return nil, err
 	}
```

### localbridgesync/mock_downloader_test.go
```diff
@@ -65,6 +65,20 @@ func (_m *DownloaderMock) getLogs(ctx context.Context, fromBlock uint64, toBlock
 	return r0
 }
 
+// syncBlockChunkSize provides a mock function with given fields:
+func (_m *DownloaderMock) syncBlockChunkSize() uint64 {
+	ret := _m.Called()
+
+	var r0 uint64
+	if rf, ok := ret.Get(0).(func() uint64); ok {
+		r0 = rf()
+	} else {
+		r0 = ret.Get(0).(uint64)
+	}
+
+	return r0
+}
+
 // waitForNewBlocks provides a mock function with given fields: ctx, lastBlockSeen
 func (_m *DownloaderMock) waitForNewBlocks(ctx context.Context, lastBlockSeen uint64) uint64 {
 	ret := _m.Called(ctx, lastBlockSeen)
```

### localbridgesync/mock_reorgdetector_test.go
```diff
@@ -12,7 +12,7 @@ import (
 	reorgdetector "github.com/0xPolygon/cdk/reorgdetector"
 )
 
-// ReorgDetectorMock is an autogenerated mock type for the reorgDetectorInterface type
+// ReorgDetectorMock is an autogenerated mock type for the ReorgDetector type
 type ReorgDetectorMock struct {
 	mock.Mock
 }
```
