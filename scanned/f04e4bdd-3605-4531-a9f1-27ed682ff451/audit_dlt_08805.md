# [?] Fix/3203 panic if batch process fail and must be closed (#3206) (#3216)

## Summary
Severity: Unknown
Chain: Polygon zkEVM
Component: 0xPolygon/zkevm-node
Published: 2024-02-06
Source: https://github.com/0xPolygon/zkevm-node/commit/d6d4b965aeb8b227b5b1da53d139c5d7d4338665
Type: security-commit

## Details
Fix/3203 panic if batch process fail and must be closed (#3206) (#3216)

* synchronizer avoid panic if process trusted batch fails

## Patch
### synchronizer/l2_sync/l2_shared/processor_trusted_batch_sync.go
```diff
@@ -218,7 +218,7 @@ func (s *ProcessorTrustedBatchSync) ExecuteProcessBatch(ctx context.Context, pro
 		log.Debugf("%s is partially synchronized but we don't have intermediate stateRoot so it needs to be fully reprocessed", processMode.DebugPrefix)
 		processBatchResp, err = s.Steps.ReProcess(ctx, processMode, dbTx)
 	}
-	if processMode.BatchMustBeClosed {
+	if processBatchResp != nil && err == nil && processMode.BatchMustBeClosed {
 		err = checkProcessBatchResultMatchExpected(processMode, processBatchResp.ProcessBatchResponse)
 		if err != nil {
 			log.Error("%s error verifying batch result!  Error: ", processMode.DebugPrefix, err)
```

### synchronizer/l2_sync/l2_shared/tests/processor_trusted_batch_sync_test.go
```diff
@@ -1,6 +1,8 @@
 package test_l2_shared
 
 import (
+	"context"
+	"errors"
 	"testing"
 
 	"github.com/0xPolygonHermez/zkevm-node/jsonrpc/types"
@@ -9,6 +11,7 @@ import (
 	"github.com/0xPolygonHermez/zkevm-node/synchronizer/l2_sync/l2_shared"
 	mock_l2_shared "github.com/0xPolygonHermez/zkevm-node/synchronizer/l2_sync/l2_shared/mocks"
 	"github.com/ethereum/go-ethereum/common"
+	"github.com/stretchr/testify/mock"
 	"github.com/stretchr/testify/require"
 )
 
@@ -321,3 +324,16 @@ func TestGetNextStatusUpdateExecutionResult(t *testing.T) {
 	require.NoError(t, err)
 	require.Equal(t, common.HexToHash("0x123"), newStatus.LastTrustedBatches[0].StateRoot)
 }
+
+func TestExecuteProcessBatchError(t *testing.T) {
+	testData := newTestDataForProcessorTrustedBatchSync(t)
+
+	data := l2_shared.ProcessData{
+		Mode:              l2_shared.NothingProcessMode,
+		BatchMustBeClosed: true,
+	}
+	returnedError := errors.New("error")
+	testData.mockExecutor.EXPECT().NothingProcess(mock.Anything, mock.Anything, mock.Anything).Return(nil, returnedError)
+	_, err := testData.sut.ExecuteProcessBatch(context.Background(), &data, nil)
+	require.ErrorIs(t, returnedError, err)
+}
```
