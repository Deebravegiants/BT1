# [?] Cherry pick: Synchronizer  PR #3584,  #3582. Fix panic and stop sync from Trusted after a open batch (#3586)

## Summary
Severity: Unknown
Chain: Polygon zkEVM
Component: 0xPolygonHermez/zkevm-node
Published: 2024-04-23
Source: https://github.com/0xPolygon/zkevm-node/commit/7ddcb2987b7ac3fbc8b43b5c9a27475c686ee903
Type: security-commit

## Details
Cherry pick: Synchronizer  PR #3584,  #3582. Fix panic and stop sync from Trusted after a open batch (#3586)

* synchronized: #3583  stop sync from l2 after no closed batch (#3584)
* fix #3581 synchronizer panic synchronizing from trusted node (#3582)

## Patch
### synchronizer/l2_sync/l2_shared/processor_trusted_batch_sync.go
```diff
@@ -171,6 +171,10 @@ func (s *ProcessorTrustedBatchSync) AddPostChecker(checker PostClosedBatchChecke
 
 // ProcessTrustedBatch processes a trusted batch and return the new state
 func (s *ProcessorTrustedBatchSync) ProcessTrustedBatch(ctx context.Context, trustedBatch *types.Batch, status TrustedState, dbTx pgx.Tx, debugPrefix string) (*TrustedState, error) {
+	if trustedBatch == nil {
+		log.Errorf("%s trustedBatch is nil, it never should be nil", debugPrefix)
+		return nil, fmt.Errorf("%s trustedBatch is nil, it never should be nil", debugPrefix)
+	}
 	log.Debugf("%s Processing trusted batch: %v", debugPrefix, trustedBatch.Number)
 	stateCurrentBatch, statePreviousBatch := s.GetCurrentAndPreviousBatchFromCache(&status)
 	if s.l1SyncChecker != nil {
@@ -374,7 +378,9 @@ func (s *ProcessorTrustedBatchSync) GetModeForProcessBatch(trustedNodeBatch *typ
 	result.OldAccInputHash = statePreviousBatch.AccInputHash
 	result.Now = s.timeProvider.Now()
 	result.DebugPrefix = fmt.Sprintf("%s mode %s:", debugPrefix, result.Mode)
-
+	if result.BatchMustBeClosed {
+		result.DebugPrefix += " (must_be_closed)"
+	}
 	if isTrustedBatchEmptyAndClosed(trustedNodeBatch) {
 		if s.Cfg.AcceptEmptyClosedBatches {
 			log.Infof("%s Batch %v: TrustedBatch Empty and closed, accepted due configuration", result.DebugPrefix, trustedNodeBatch.Number)
```

### synchronizer/l2_sync/l2_shared/tests/trusted_batches_retrieve_test.go
```diff
@@ -0,0 +1,117 @@
+package test_l2_shared
+
+import (
+	"context"
+	"math/big"
+	"testing"
+
+	"github.com/0xPolygonHermez/zkevm-node/jsonrpc/types"
+	"github.com/0xPolygonHermez/zkevm-node/state"
+	"github.com/0xPolygonHermez/zkevm-node/synchronizer/common"
+	mock_syncinterfaces "github.com/0xPolygonHermez/zkevm-node/synchronizer/common/syncinterfaces/mocks"
+	"github.com/0xPolygonHermez/zkevm-node/synchronizer/l2_sync/l2_shared"
+	l2sharedmocks "github.com/0xPolygonHermez/zkevm-node/synchronizer/l2_sync/l2_shared/mocks"
+	syncMocks "github.com/0xPolygonHermez/zkevm-node/synchronizer/mocks"
+	"github.com/stretchr/testify/mock"
+	"github.com/stretchr/testify/require"
+)
+
+type testDataTrustedBatchRetrieve struct {
+	mockBatchProcessor *l2sharedmocks.BatchProcessor
+	mockZkEVMClient    *mock_syncinterfaces.ZKEVMClientTrustedBatchesGetter
+	mockState          *l2sharedmocks.StateInterface
+	mockSync           *mock_syncinterfaces.SynchronizerFlushIDManager
+	mockTimer          *common.MockTimerProvider
+	mockDbTx           *syncMocks.DbTxMock
+	TrustedStateMngr   *l2_shared.TrustedStateManager
+	sut                *l2_shared.TrustedBatchesRetrieve
+	ctx                context.Context
+}
+
+func newTestDataTrustedBatchRetrieve(t *testing.T) *testDataTrustedBatchRetrieve {
+	mockBatchProcessor := l2sharedmocks.NewBatchProcessor(t)
+	mockZkEVMClient := mock_syncinterfaces.NewZKEVMClientTrustedBatchesGetter(t)
+	mockState := l2sharedmocks.NewStateInterface(t)
+	mockSync := mock_syncinterfaces.NewSynchronizerFlushIDManager(t)
+	mockTimer := &common.MockTimerProvider{}
+	mockDbTx := syncMocks.NewDbTxMock(t)
+	TrustedStateMngr := l2_shared.NewTrustedStateManager(mockTimer, 0)
+	sut := l2_shared.NewTrustedBatchesRetrieve(mockBatchProcessor, mockZkEVMClient, mockState, mockSync, *TrustedStateMngr)
+	ctx := context.TODO()
+	return &testDataTrustedBatchRetrieve{
+		mockBatchProcessor: mockBatchProcessor,
+		mockZkEVMClient:    mockZkEVMClient,
+		mockState:          mockState,
+		mockSync:           mockSync,
+		mockTimer:          mockTimer,
+		mockDbTx:           mockDbTx,
+		TrustedStateMngr:   TrustedStateMngr,
+		sut:                sut,
+		ctx:                ctx,
+	}
+}
+
+const (
+	closedBatch    = true
+	notClosedBatch = false
+)
+
+// This test must do from 100 to 104.
+// But the batch 100 is open on TrustedNode so it stop processing
+func TestSyncTrustedBatchesToFromStopAfterFirstWIPBatch(t *testing.T) {
+	data := newTestDataTrustedBatchRetrieve(t)
+	data.mockZkEVMClient.EXPECT().BatchNumber(data.ctx).Return(uint64(102), nil)
+
+	expectationsForSyncTrustedStateIteration(t, 100, notClosedBatch, data)
+
+	err := data.sut.SyncTrustedState(data.ctx, 100, 104)
+	require.NoError(t, err)
+}
+
+// This must process 100 (that is closed)
+// and stop processing at 101 because is not yet close this batch
+func TestSyncTrustedBatchesToFromStopAfterFirstWIPBatchCase2(t *testing.T) {
+	data := newTestDataTrustedBatchRetrieve(t)
+	data.mockZkEVMClient.EXPECT().BatchNumber(data.ctx).Return(uint64(102), nil)
+
+	expectationsForSyncTrustedStateIteration(t, 100, closedBatch, data)
+	expectationsForSyncTrustedStateIteration(t, 101, notClosedBatch, data)
+
+	err := data.sut.SyncTrustedState(data.ctx, 100, 104)
+	require.NoError(t, err)
+}
+
+// This test must do from 100 to 102. Is for check manually that the logs
+// That is not tested but must not emit the log:
+//   - Batch 101 is not closed. so we break synchronization from Trusted Node because can only have 1 WIP batch on state
+func TestSyncTrustedBatchesToFromStopAfterFirstWIPBatchCase3(t *testing.T) {
+	data := newTestDataTrustedBatchRetrieve(t)
+	data.mockZkEVMClient.EXPECT().BatchNumber(data.ctx).Return(uint64(102), nil)
+	expectationsForSyncTrustedStateIteration(t, 100, closedBatch, data)
+	expectationsForSyncTrustedStateIteration(t, 101, closedBatch, data)
+	expectationsForSyncTrustedStateIteration(t, 102, notClosedBatch, data)
+
+	err := data.sut.SyncTrustedState(data.ctx, 100, 102)
+	require.NoError(t, err)
+}
+
+func expectationsForSyncTrustedStateIteration(t *testing.T, batchNumber uint64, closed bool, data *testDataTrustedBatchRetrieve) {
+	batch100 := &types.Batch{
+		Number: types.ArgUint64(batchNumber),
+		Closed: closed,
+	}
+	data.mockZkEVMClient.EXPECT().BatchByNumber(data.ctx, big.NewInt(0).SetUint64(batchNumber)).Return(batch100, nil)
+	data.mockState.EXPECT().BeginStateTransaction(data.ctx).Return(data.mockDbTx, nil)
+	// Get Previous Batch 99 from State
+	stateBatch99 := &state.Batch{
+		BatchNumber: batchNumber - 1,
+	}
+	data.mockState.EXPECT().GetBatchByNumber(data.ctx, uint64(batchNumber-1), data.mockDbTx).Return(stateBatch99, nil)
+	stateBatch100 := &state.Batch{
+		BatchNumber: batchNumber,
+	}
+	data.mockState.EXPECT().GetBatchByNumber(data.ctx, uint64(batchNumber), data.mockDbTx).Return(stateBatch100, nil)
+	data.mockBatchProcessor.EXPECT().ProcessTrustedBatch(data.ctx, mock.Anything, mock.Anything, mock.Anything, mock.Anything).Return(nil, nil)
+	data.mockSync.EXPECT().CheckFlushID(mock.Anything).Return(nil)
+	data.mockDbTx.EXPECT().Commit(data.ctx).Return(nil)
+}
```

### synchronizer/l2_sync/l2_shared/trusted_batches_retrieve.go
```diff
@@ -109,6 +109,16 @@ func isSyncrhonizedTrustedState(lastTrustedStateBatchNumber uint64, latestSynced
 	return lastTrustedStateBatchNumber < latestSyncedBatch
 }
 
+func sanityCheckBatchReturnedByTrusted(batch *types.Batch, expectedBatchNumber uint64) error {
+	if batch == nil {
+		return fmt.Errorf("batch %d is nil", expectedBatchNumber)
+	}
+	if uint64(batch.Number) != expectedBatchNumber {
+		return fmt.Errorf("batch %d is not the expected batch %d", batch.Number, expectedBatchNumber)
+	}
+	return nil
+}
+
 func (s *TrustedBatchesRetrieve) syncTrustedBatchesToFrom(ctx context.Context, latestSyncedBatch uint64, lastTrustedStateBatchNumber uint64) error {
 	batchNumberToSync := max(latestSyncedBatch, s.firstBatchNumberToSync)
 	for batchNumberToSync <= lastTrustedStateBatchNumber {
@@ -120,6 +130,11 @@ func (s *TrustedBatchesRetrieve) syncTrustedBatchesToFrom(ctx context.Context, l
 			log.Warnf("%s failed to get batch %d from trusted state. Error: %v", debugPrefix, batchNumberToSync, err)
 			return err
 		}
+		err = sanityCheckBatchReturnedByTrusted(batchToSync, batchNumberToSync)
+		if err != nil {
+			log.Warnf("%s sanity check over Batch returned by Trusted-RPC failed: %v", debugPrefix, err)
+			return err
+		}
 
 		dbTx, err := s.state.BeginStateTransaction(ctx)
 		if err != nil {
@@ -161,6 +176,10 @@ func (s *TrustedBatchesRetrieve) syncTrustedBatchesToFrom(ctx context.Context, l
 			s.TrustedStateMngr.Clear()
 		}
 		batchNumberToSync++
+		if !batchToSync.Closed && batchNumberToSync <= lastTrustedStateBatchNumber {
+			log.Infof("%s Batch %d is not closed. so we break synchronization from Trusted Node because can only have 1 WIP batch on state", debugPrefix, batchToSync.Number)
+			return nil
+		}
 	}
 
 	log.Infof("syncTrustedState: Trusted state fully synchronized from %d to %d", latestSyncedBatch, lastTrustedStateBatchNumber)
```
