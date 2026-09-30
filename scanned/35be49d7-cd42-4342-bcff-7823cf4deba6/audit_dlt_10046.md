# [?] Merge pull request #7702 from multiversx/fix-unsigned-nonce-gap-underflow

## Summary
Severity: Unknown
Chain: MultiversX
Component: multiversx/mx-chain-go
Published: 2026-02-12
Source: https://github.com/multiversx/mx-chain-go/commit/f36e9b99c75f2d8db49c054fe6efc8d05f5bd5dd
Type: security-commit

## Details
Merge pull request #7702 from multiversx/fix-unsigned-nonce-gap-underflow

HIGH-005: prevent nonce gap underflow

## Patch
### process/asyncExecution/executionManager/executionManager.go
```diff
@@ -12,10 +12,10 @@ import (
 
 	"github.com/multiversx/mx-chain-go/dataRetriever"
 	"github.com/multiversx/mx-chain-go/process"
+	"github.com/multiversx/mx-chain-go/process/asyncExecution/cache"
 	"github.com/multiversx/mx-chain-go/process/asyncExecution/disabled"
 	"github.com/multiversx/mx-chain-go/sharding"
-
-	"github.com/multiversx/mx-chain-go/process/asyncExecution/cache"
+	"github.com/multiversx/mx-chain-go/storage"
 )
 
 var log = logger.GetOrCreate("process/asyncExecution/executionManager")
@@ -203,19 +203,7 @@ func (em *executionManager) RemoveAtNonceAndHigher(nonce uint64) error {
 	em.headersExecutor.PauseExecution()
 
 	// remove from queue
-	removedNonces := em.blocksCache.RemoveAtNonceAndHigher(nonceToRemove)
-	if len(removedNonces) > 0 && removedNonces[0] == nonceToRemove {
-		// if the first nonce removed is the initial one,
-		// it means it was still in queue and was not processed.
-		// no matter how many were removed, safe to resume execution
-		em.headersExecutor.ResumeExecution()
-
-		return nil
-	}
-
-	// if the initial nonce was not returned as removed from the queue,
-	// it means that it was already popped for execution (and perhaps not the only one).
-	// inform executionResultsTracker to remove all nonces >= than the provided one
+	_ = em.blocksCache.RemoveAtNonceAndHigher(nonceToRemove)
 	err = em.executionResultsTracker.RemoveFromNonce(nonceToRemove)
 	if err != nil {
 		return err
```

### process/asyncExecution/executionManager/executionManager_test.go
```diff
@@ -657,13 +657,26 @@ func TestExecutionManager_RemoveAtNonceAndHigher(t *testing.T) {
 		args := createMockArgs()
 		pauseCalled := false
 		resumeCalled := false
+		removeFromNonceCalled := false
+
+		lastNotarizedExecResult := &block.ExecutionResult{
+			BaseExecutionResult: &block.BaseExecutionResult{
+				HeaderNonce: 10,
+				HeaderHash:  []byte("hash10"),
+				RootHash:    []byte("root10"),
+			},
+		}
 		args.ExecutionResultsTracker = &processMocks.ExecutionTrackerStub{
 			GetLastNotarizedExecutionResultCalled: func() (data.BaseExecutionResultHandler, error) {
-				return &block.ExecutionResult{
-					BaseExecutionResult: &block.BaseExecutionResult{
-						HeaderNonce: 10,
-					},
-				}, nil
+				return lastNotarizedExecResult, nil
+			},
+			RemoveFromNonceCalled: func(nonce uint64) error {
+				removeFromNonceCalled = true
+				require.Equal(t, uint64(11), nonce)
+				return nil
+			},
+			GetPendingExecutionResultsCalled: func() ([]data.BaseExecutionResultHandler, error) {
+				return []data.BaseExecutionResultHandler{}, nil
 			},
 		}
 		args.BlocksCache = &processMocks.BlocksCacheMock{
@@ -673,6 +686,15 @@ func TestExecutionManager_RemoveAtNonceAndHigher(t *testing.T) {
 				return []uint64{11}
 			},
 		}
+		header := &block.Header{Nonce: 10}
+		args.Headers = &pool.HeadersPoolStub{
+			GetHeaderByHashCalled: func(hash []byte) (data.HeaderHandler, error) {
+				return header, nil
+			},
+		}
+		chainMock := &testscommon.ChainHandlerMock{}
+		args.BlockChain = chainMock
+
 		em, _ := executionManager.NewExecutionManager(args)
 		mockExecutor := &processMocks.HeadersExecutorMock{
 			PauseExecutionCalled: func() {
@@ -688,34 +710,59 @@ func TestExecutionManager_RemoveAtNonceAndHigher(t *testing.T) {
 		require.NoError(t, err)
 		require.True(t, pauseCalled)
 		require.True(t, resumeCalled)
+		require.True(t, removeFromNonceCalled)
+
+		// Verify blockchain was updated to last notarized state
+		nonce, hash, rootHash := chainMock.GetFinalBlockInfo()
+		require.Equal(t, uint64(10), nonce)
+		require.Equal(t, []byte("hash10"), hash)
+		require.Equal(t, []byte("root10"), rootHash)
 	})
 
-	t.Run("nonce still in queue should resume execution", func(t *testing.T) {
+	t.Run("nonce still in cache should still perform cleanup", func(t *testing.T) {
 		t.Parallel()
 
 		args := createMockArgs()
 		pauseCalled := false
 		resumeCalled := false
+		removeFromNonceCalled := false
+
+		lastNotarizedExecResult := &block.ExecutionResult{
+			BaseExecutionResult: &block.BaseExecutionResult{
+				HeaderNonce: 9,
+				HeaderHash:  []byte("hash9"),
+				RootHash:    []byte("root9"),
+			},
+		}
 		args.ExecutionResultsTracker = &processMocks.ExecutionTrackerStub{
 			GetLastNotarizedExecutionResultCalled: func() (data.BaseExecutionResultHandler, error) {
-				return &block.ExecutionResult{
-					BaseExecutionResult: &block.BaseExecutionResult{
-						HeaderNonce: 9,
-					},
-				}, nil
+				return lastNotarizedExecResult, nil
 			},
 			RemoveFromNonceCalled: func(nonce uint64) error {
-				require.Fail(t, "should not have been called")
+				removeFromNonceCalled = true
+				require.Equal(t, uint64(10), nonce)
 				return nil
 			},
+			GetPendingExecutionResultsCalled: func() ([]data.BaseExecutionResultHandler, error) {
+				return []data.BaseExecutionResultHandler{}, nil
+			},
 		}
 		args.BlocksCache = &processMocks.BlocksCacheMock{
 			RemoveAtNonceAndHigherCalled: func(nonce uint64) []uint64 {
 				require.Equal(t, uint64(10), nonce)
-				// First removed nonce matches the requested nonce
+				// First removed nonce matches the requested nonce (block still in cache)
 				return []uint64{10, 11, 12}
 			},
 		}
+		header := &block.Header{Nonce: 9}
+		args.Headers = &pool.HeadersPoolStub{
+			GetHeaderByHashCalled: func(hash []byte) (data.HeaderHandler, error) {
+				return header, nil
+			},
+		}
+		chainMock := &testscommon.ChainHandlerMock{}
+		args.BlockChain = chainMock
+
 		em, _ := executionManager.NewExecutionManager(args)
 		mockExecutor := &processMocks.HeadersExecutorMock{
 			PauseExecutionCalled: func() {
@@ -731,6 +778,16 @@ func TestExecutionManager_RemoveAtNonceAndHigher(t *testing.T) {
 		require.NoError(t, err)
 		require.True(t, pauseCalled)
 		require.True(t, resumeCalled)
+		require.True(t, removeFromNonceCalled)
+
+		// Verify blockchain was updated to last notarized state
+		nonce, hash, rootHash := chainMock.GetFinalBlockInfo()
+		require.Equal(t, uint64(9), nonce)
+		require.Equal(t, []byte("hash9"), hash)
+		require.Equal(t, []byte("root9"), rootHash)
+
+		retLastExecutionResult := chainMock.GetLastExecutionResult()
+		require.Equal(t, lastNotarizedExecResult, retLastExecutionResult)
 	})
 
 	t.Run("nonce already popped should clean tracker and update blockchain", func(t *testing.T) {
@@ -804,6 +861,90 @@ func TestExecutionManager_RemoveAtNonceAndHigher(t *testing.T) {
 		require.Equal(t, lastNotarizedExecResult, retLastExecutionResult)
 	})
 
+	t.Run("nonce in cache and already processed should clean tracker and update blockchain", func(t *testing.T) {
+		t.Parallel()
+
+		args := createMockArgs()
+		pauseCalled := false
+		resumeCalled := false
+		removeFromNonceCalled := false
+
+		// Block at nonce 10 was processed, execution result exists as pending
+		pendingExecResult := &block.BaseExecutionResult{
+			HeaderNonce: 10,
+			HeaderHash:  []byte("hash10"),
+			RootHash:    []byte("root10"),
+		}
+		lastNotarizedExecResult := &block.ExecutionResult{
+			BaseExecutionResult: &block.BaseExecutionResult{
+				HeaderNonce: 9,
+				HeaderHash:  []byte("hash9"),
+				RootHash:    []byte("root9"),
+			},
+		}
+		removePendingCalled := false
+		args.ExecutionResultsTracker = &processMocks.ExecutionTrackerStub{
+			GetLastNotarizedExecutionResultCalled: func() (data.BaseExecutionResultHandler, error) {
+				return lastNotarizedExecResult, nil
+			},
+			RemoveFromNonceCalled: func(nonce uint64) error {
+				removeFromNonceCalled = true
+				require.Equal(t, uint64(10), nonce)
+				removePendingCalled = true
+				return nil
+			},
+			GetPendingExecutionResultsCalled: func() ([]data.BaseExecutionResultHandler, error) {
+				if removePendingCalled {
+					// after RemoveFromNonce, pending is empty
+					return []data.BaseExecutionResultHandler{}, nil
+				}
+				// before removal, pending has the processed result
+				return []data.BaseExecutionResultHandler{pendingExecResult}, nil
+			},
+		}
+		args.BlocksQueue = &processMocks.BlocksQueueMock{
+			RemoveAtNonceAndHigherCalled: func(nonce uint64) []uint64 {
+				require.Equal(t, uint64(10), nonce)
+				// Block was still in cache but was already processed by headersExecutor
+				return []uint64{10}
+			},
+		}
+		header := &block.Header{Nonce: 9}
+		args.Headers = &pool.HeadersPoolStub{
+			GetHeaderByHashCalled: func(hash []byte) (data.HeaderHandler, error) {
+				return header, nil
+			},
+		}
+		chainMock := &testscommon.ChainHandlerMock{}
+		args.BlockChain = chainMock
+
+		em, _ := executionManager.NewExecutionManager(args)
+		mockExecutor := &processMocks.HeadersExecutorMock{
+			PauseExecutionCalled: func() {
+				pauseCalled = true
+			},
+			ResumeExecutionCalled: func() {
+				resumeCalled = true
+			},
+		}
+		_ = em.SetHeadersExecutor(mockExecutor)
+
+		err := em.RemoveAtNonceAndHigher(10)
+		require.NoError(t, err)
+		require.True(t, pauseCalled)
+		require.True(t, resumeCalled)
+		require.True(t, removeFromNonceCalled)
+
+		// Verify blockchain was rolled back to last notarized state
+		nonce, hash, rootHash := chainMock.GetFinalBlockInfo()
+		require.Equal(t, uint64(9), nonce)
+		require.Equal(t, []byte("hash9"), hash)
+		require.Equal(t, []byte("root9"), rootHash)
+
+		retLastExecutionResult := chainMock.GetLastExecutionResult()
+		require.Equal(t, lastNotarizedExecResult, retLastExecutionResult)
+	})
+
 	t.Run("error from tracker remove should error", func(t *testing.T) {
 		t.Parallel()
 
```

### process/missingData/missingDataResolver.go
```diff
@@ -322,8 +322,16 @@ func (r *Resolver) requestNonceGapsIfNeeded(shardDataFinalizedNonces, shardDataP
 			continue
 		}
 
-		nonceGaps := proposedNonce - lastFinalizedNonce
-		if nonceGaps < 2 {
+		if proposedNonce <= lastFinalizedNonce {
+			log.Warn("requestNonceGapsIfNeeded: proposed nonce is not greater than finalized nonce, skipping",
+				"shardID", shardID,
+				"proposedNonce", proposedNonce,
+				"lastFinalizedNonce", lastFinalizedNonce)
+			continue
+		}
+
+		nonceGap := proposedNonce - lastFinalizedNonce
+		if nonceGap < 2 {
 			continue
 		}
 
```

### process/missingData/missingDataResolver_test.go
```diff
@@ -3,6 +3,7 @@ package missingData
 import (
 	"errors"
 	"fmt"
+	"math"
 	"sync"
 	"testing"
 	"time"
@@ -1015,6 +1016,484 @@ func TestResolver_Reset(t *testing.T) {
 	require.True(t, called)
 }
 
+func TestResolver_requestNonceGapsIfNeeded(t *testing.T) {
+	t.Parallel()
+
+	t.Run("proposed nonce less than finalized nonce should not request (underflow prevention)", func(t *testing.T) {
+		t.Parallel()
+
+		numRequests := 0
+		headersPool := &pool.HeadersPoolStub{}
+		proofsPool := &dataRetriever.ProofsPoolMock{}
+		requestHandler := &testscommon.RequestHandlerStub{
+			RequestShardHeaderByNonceCalled: func(_ uint32, _ uint64) {
+				numRequests++
+			},
+			RequestEquivalentProofByNonceCalled: func(_ uint32, _ uint64) {
+				numRequests++
+			},
+		}
+		blockDataRequester := &preprocMocks.BlockDataRequesterStub{}
+		args := ResolverArgs{
+			HeadersPool:        headersPool,
+			ProofsPool:         proofsPool,
+			RequestHandler:     requestHandler,
+			BlockDataRequester: blockDataRequester,
+		}
+		mdr, _ := NewMissingDataResolver(args)
+
+		finalizedNonces := map[uint32]uint64{0: 10}
+		proposedNonces := map[uint32]uint64{0: 5}
+		mdr.requestNonceGapsIfNeeded(finalizedNonces, proposedNonces)
+
+		require.Equal(t, 0, numRequests)
+	})
+
+	t.Run("proposed nonce equal to finalized nonce should not request", func(t *testing.T) {
+		t.Parallel()
+
+		numRequests := 0
+		headersPool := &pool.HeadersPoolStub{}
+		proofsPool := &dataRetriever.ProofsPoolMock{}
+		requestHandler := &testscommon.RequestHandlerStub{
+			RequestShardHeaderByNonceCalled: func(_ uint32, _ uint64) {
+				numRequests++
+			},
+			RequestEquivalentProofByNonceCalled: func(_ uint32, _ uint64) {
+				numRequests++
+			},
+		}
+		blockDataRequester := &preprocMocks.BlockDataRequesterStub{}
+		args := ResolverArgs{
+			HeadersPool:        headersPool,
+			ProofsPool:         proofsPool,
+			RequestHandler:     requestHandler,
+			BlockDataRequester: blockDataRequester,
+		}
+		mdr, _ := NewMissingDataResolver(args)
+
+		finalizedNonces := map[uint32]uint64{0: 10}
+		proposedNonces := map[uint32]uint64{0: 10}
+		mdr.requestNonceGapsIfNeeded(finalizedNonces, proposedNonces)
+
+		require.Equal(t, 0, numRequests)
+	})
+
+	t.Run("proposed nonce is finalized+1, gap of 1 should not request", func(t *testing.T) {
+		t.Parallel()
+
+		numRequests := 0
+		headersPool := &pool.HeadersPoolStub{}
+		proofsPool := &dataRetriever.ProofsPoolMock{}
+		requestHandler := &testscommon.RequestHandlerStub{
+			RequestShardHeaderByNonceCalled: func(_ uint32, _ uint64) {
+				numRequests++
+			},
+			RequestEquivalentProofByNonceCalled: func(_ uint32, _ uint64) {
+				numRequests++
+			},
+		}
+		blockDataRequester := &preprocMocks.BlockDataRequesterStub{}
+		args := ResolverArgs{
+			HeadersPool:        headersPool,
+			ProofsPool:         proofsPool,
+			RequestHandler:     requestHandler,
+			BlockDataRequester: blockDataRequester,
+		}
+		mdr, _ := NewMissingDataResolver(args)
+
+		finalizedNonces := map[uint32]uint64{0: 10}
+		proposedNonces := map[uint32]uint64{0: 11}
+		mdr.requestNonceGapsIfNeeded(finalizedNonces, proposedNonces)
+
+		require.Equal(t, 0, numRequests)
+	})
+
+	t.Run("MaxUint64 finalized with MaxUint64-1 proposed should not request (underflow scenario)", func(t *testing.T) {
+		t.Parallel()
+
+		numRequests := 0
+		headersPool := &pool.HeadersPoolStub{}
+		proofsPool := &dataRetriever.ProofsPoolMock{}
+		requestHandler := &testscommon.RequestHandlerStub{
+			RequestShardHeaderByNonceCalled: func(_ uint32, _ uint64) {
+				numRequests++
+			},
+			RequestEquivalentProofByNonceCalled: func(_ uint32, _ uint64) {
+				numRequests++
+			},
+		}
+		blockDataRequester := &preprocMocks.BlockDataRequesterStub{}
+		args := ResolverArgs{
+			HeadersPool:        headersPool,
+			ProofsPool:         proofsPool,
+			RequestHandler:     requestHandler,
+			BlockDataRequester: blockDataRequester,
+		}
+		mdr, _ := NewMissingDataResolver(args)
+
+		finalizedNonces := map[uint32]uint64{0: math.MaxUint64}
+		proposedNonces := map[uint32]uint64{0: math.MaxUint64 - 1}
+		mdr.requestNonceGapsIfNeeded(finalizedNonces, proposedNonces)
+
+		require.Equal(t, 0, numRequests)
+	})
+
+	t.Run("normal gap of 2 should request exactly 1 nonce", func(t *testing.T) {
+		t.Parallel()
+
+		requestedNonces := make([]uint64, 0)
+		mut := sync.Mutex{}
+		headerNotFoundErr := errors.New("not found")
+		headersPool := &pool.HeadersPoolStub{
+			GetHeaderByNonceAndShardIdCalled: func(_ uint64, _ uint32) ([]data.HeaderHandler, [][]byte, error) {
+				return nil, nil, headerNotFoundErr
+			},
+		}
+		proofsPool := &dataRetriever.ProofsPoolMock{
+			GetProofByNonceCalled: func(_ uint64, _ uint32) (data.HeaderProofHandler, error) {
+				return nil, headerNotFoundErr
+			},
+		}
+		requestHandler := &testscommon.RequestHandlerStub{
+			RequestShardHeaderByNonceCalled: func(shardID uint32, nonce uint64) {
+				mut.Lock()
+				requestedNonces = append(requestedNonces, nonce)
+				mut.Unlock()
+			},
+			RequestEquivalentProofByNonceCalled: func(_ uint32, _ uint64) {},
+		}
+		blockDataRequester := &preprocMocks.BlockDataRequesterStub{}
+		args := ResolverArgs{
+			HeadersPool:        headersPool,
+			ProofsPool:         proofsPool,
+			RequestHandler:     requestHandler,
+			BlockDataRequester: blockDataRequester,
+		}
+		mdr, _ := NewMissingDataResolver(args)
+
+		// finalized=5, proposed=7: gap=2, should request nonce 6
+		finalizedNonces := map[uint32]uint64{0: 5}
+		proposedNonces := map[uint32]uint64{0: 7}
+		mdr.requestNonceGapsIfNeeded(finalizedNonces, proposedNonces)
+
+		// wait for goroutines spawned by requestShardHeaderByNonceIfNeeded
+		time.Sleep(50 * time.Millisecond)
+
+		mut.Lock()
+		require.Equal(t, []uint64{6}, requestedNonces)
+		mut.Unlock()
+	})
+
+	t.Run("shard not found in finalized nonces should not request", func(t *testing.T) {
+		t.Parallel()
+
+		numRequests := 0
+		headersPool := &pool.HeadersPoolStub{}
+		proofsPool := &dataRetriever.ProofsPoolMock{}
+		requestHandler := &testscommon.RequestHandlerStub{
+			RequestShardHeaderByNonceCalled: func(_ uint32, _ uint64) {
+				numRequests++
+			},
+			RequestEquivalentProofByNonceCalled: func(_ uint32, _ uint64) {
+				numRequests++
+			},
+		}
+		blockDataRequester := &preprocMocks.BlockDataRequesterStub{}
+		args := ResolverArgs{
+			HeadersPool:        headersPool,
+			ProofsPool:         proofsPool,
+			RequestHandler:     requestHandler,
+			BlockDataRequester: blockDataRequester,
+		}
+		mdr, _ := NewMissingDataResolver(args)
+
+		// proposed has shard 0, finalized has shard 1 - no match
+		finalizedNonces := map[uint32]uint64{1: 5}
+		proposedNonces := map[uint32]uint64{0: 10}
+		mdr.requestNonceGapsIfNeeded(finalizedNonces, proposedNonces)
+
+		require.Equal(t, 0, numRequests)
+	})
+
+	t.Run("finalized nonce 0 proposed nonce 0 should not request", func(t *testing.T) {
+		t.Parallel()
+
+		numRequests := 0
+		headersPool := &pool.HeadersPoolStub{}
+		proofsPool := &dataRetriever.ProofsPoolMock{}
+		requestHandler := &testscommon.RequestHandlerStub{
+			RequestShardHeaderByNonceCalled: func(_ uint32, _ uint64) {
+				numRequests++
+			},
+			RequestEquivalentProofByNonceCalled: func(_ uint32, _ uint64) {
+				numRequests++
+			},
+		}
+		blockDataRequester := &preprocMocks.BlockDataRequesterStub{}
+		args := ResolverArgs{
+			HeadersPool:        headersPool,
+			ProofsPool:         proofsPool,
+			RequestHandler:     requestHandler,
+			BlockDataRequester: blockDataRequester,
+		}
+		mdr, _ := NewMissingDataResolver(args)
+
+		finalizedNonces := map[uint32]uint64{0: 0}
+		proposedNonces := map[uint32]uint64{0: 0}
+		mdr.requestNonceGapsIfNeeded(finalizedNonces, proposedNonces)
+
+		require.Equal(t, 0, numRequests)
+	})
+
+	t.Run("multiple shards with mixed valid and invalid gaps", func(t *testing.T) {
+		t.Parallel()
+
+		requestedShardNonces := make(map[uint32][]uint64)
+		mut := sync.Mutex{}
+		headerNotFoundErr := errors.New("not found")
+		headersPool := &pool.HeadersPoolStub{
+			GetHeaderByNonceAndShardIdCalled: func(_ uint64, _ uint32) ([]data.HeaderHandler, [][]byte, error) {
+				return nil, nil, headerNotFoundErr
+			},
+		}
+		proofsPool := &dataRetriever.ProofsPoolMock{
+			GetProofByNonceCalled: func(_ uint64, _ uint32) (data.HeaderProofHandler, error) {
+				return nil, headerNotFoundErr
+			},
+		}
+		requestHandler := &testscommon.RequestHandlerStub{
+			RequestShardHeaderByNonceCalled: func(shardID uint32, nonce uint64) {
+				mut.Lock()
+				requestedShardNonces[shardID] = append(requestedShardNonces[shardID], nonce)
+				mut.Unlock()
+			},
+			RequestEquivalentProofByNonceCalled: func(_ uint32, _ uint64) {},
+		}
+		blockDataRequester := &preprocMocks.BlockDataRequesterStub{}
+		args := ResolverArgs{
+			HeadersPool:        headersPool,
+			ProofsPool:         proofsPool,
+			RequestHandler:     requestHandler,
+			BlockDataRequester: blockDataRequester,
+		}
+		mdr, _ := NewMissingDataResolver(args)
+
+		finalizedNonces := map[uint32]uint64{
+			0: 10,             // shard 0: valid gap of 3
+			1: 20,             // shard 1: proposed < finalized (invalid)
+			2: math.MaxUint64, // shard 2: underflow scenario (invalid)
+		}
+		proposedNonces := map[uint32]uint64{
+			0: 13,                 // gap=3, valid
+			1: 5,                  // proposed < finalized, should skip
+			2: math.MaxUint64 - 1, // underflow, should skip
+		}
+		mdr.requestNonceGapsIfNeeded(finalizedNonces, proposedNonces)
+
+		// wait for goroutines spawned by requestShardHeaderByNonceIfNeeded
+		time.Sleep(50 * time.Millisecond)
+
+		mut.Lock()
+		// only shard 0 should have requests (nonces 11, 12)
+		require.Len(t, requestedShardNonces, 1)
+		require.ElementsMatch(t, []uint64{11, 12}, requestedShardNonces[0])
+		mut.Unlock()
+	})
+}
+
+func TestResolver_RequestMissingShardHeaders_NonceGapProtection(t *testing.T) {
+	t.Parallel()
+
+	headerNotFoundErr := errors.New("header not found")
+
+	t.Run("proposed nonce less than finalized should not trigger nonce gap requests", func(t *testing.T) {
+		t.Parallel()
+
+		nonceRequestCount := 0
+		mut := sync.Mutex{}
+
+		headersPool := &pool.HeadersPoolStub{
+			GetHeaderByHashCalled: func(_ []byte) (data.HeaderHandler, error) {
+				return nil, headerNotFoundErr
+			},
+			GetHeaderByNonceAndShardIdCalled: func(_ uint64, _ uint32) ([]data.HeaderHandler, [][]byte, error) {
+				return nil, nil, headerNotFoundErr
+			},
+		}
+		proofsPool := &dataRetriever.ProofsPoolMock{
+			HasProofCalled: func(_ uint32, _ []byte) bool { return false },
+			GetProofByNonceCalled: func(_ uint64, _ uint32) (data.HeaderProofHandler, error) {
+				return nil, headerNotFoundErr
+			},
+		}
+		requestHandler := &testscommon.RequestHandlerStub{
+			RequestShardHeaderCalled:           func(_ uint32, _ []byte) {},
+			RequestEquivalentProofByHashCalled: func(_ uint32, _ []byte) {},
+			RequestShardHeaderByNonceCalled: func(_ uint32, _ uint64) {
+				mut.Lock()
+				nonceRequestCount++
+				mut.Unlock()
+			},
+			RequestEquivalentProofByNonceCalled: func(_ uint32, _ uint64) {
+				mut.Lock()
+				nonceRequestCount++
+				mut.Unlock()
+			},
+		}
+		blockDataRequester := &preprocMocks.BlockDataRequesterStub{}
+		args := ResolverArgs{
+			HeadersPool:        headersPool,
+			ProofsPool:         proofsPool,
+			RequestHandler:     requestHandler,
+			BlockDataRequester: blockDataRequester,
+		}
+		mdr, _ := NewMissingDataResolver(args)
+
+		// byzantine node: proposed nonce 5, finalized nonce 100
+		metaHeader := &block.MetaBlockV3{
+			ShardInfoProposal: []block.ShardDataProposal{
+				{Nonce: 5, ShardID: 1, HeaderHash: []byte("hash1")},
+			},
+			ShardInfo: []block.ShardData{
+				{Nonce: 100, ShardID: 1, HeaderHash: []byte("hash2")},
+			},
+		}
+
+		err := mdr.RequestMissingShardHeaders(metaHeader)
+		require.Nil(t, err)
+
+		// wait briefly for any goroutines
+		time.Sleep(50 * time.Millisecond)
+
+		mut.Lock()
+		require.Equal(t, 0, nonceRequestCount)
+		mut.Unlock()
+	})
+
+	t.Run("MaxUint64 finalized nonce with small proposed should not trigger nonce gap requests", func(t *testing.T) {
+		t.Parallel()
+
+		nonceRequestCount := 0
+		mut := sync.Mutex{}
+
+		headersPool := &pool.HeadersPoolStub{
+			GetHeaderByHashCalled: func(_ []byte) (data.HeaderHandler, error) {
+				return nil, headerNotFoundErr
+			},
+			GetHeaderByNonceAndShardIdCalled: func(_ uint64, _ uint32) ([]data.HeaderHandler, [][]byte, error) {
+				return nil, nil, headerNotFoundErr
+			},
+		}
+		proofsPool := &dataRetriever.ProofsPoolMock{
+			HasProofCalled: func(_ uint32, _ []byte) bool { return false },
+			GetProofByNonceCalled: func(_ uint64, _ uint32) (data.HeaderProofHandler, error) {
+				return nil, headerNotFoundErr
+			},
+		}
+		requestHandler := &testscommon.RequestHandlerStub{
+			RequestShardHeaderCalled:           func(_ uint32, _ []byte) {},
+			RequestEquivalentProofByHashCalled: func(_ uint32, _ []byte) {},
+			RequestShardHeaderByNonceCalled: func(_ uint32, _ uint64) {
+				mut.Lock()
+				nonceRequestCount++
+				mut.Unlock()
+			},
+			RequestEquivalentProofByNonceCalled: func(_ uint32, _ uint64) {
+				mut.Lock()
+				nonceRequestCount++
+				mut.Unlock()
+			},
+		}
+		blockDataRequester := &preprocMocks.BlockDataRequesterStub{}
+		args := ResolverArgs{
+			HeadersPool:        headersPool,
+			ProofsPool:         proofsPool,
+			RequestHandler:     requestHandler,
+			BlockDataRequester: blockDataRequester,
+		}
+		mdr, _ := NewMissingDataResolver(args)
+
+		// byzantine meta header: MaxUint64 finalized, small proposed - would cause startNonce wrap to 0
+		metaHeader := &block.MetaBlockV3{
+			ShardInfoProposal: []block.ShardDataProposal{
+				{Nonce: 1000, ShardID: 1, HeaderHash: []byte("hash1")},
+			},
+			ShardInfo: []block.ShardData{
+				{Nonce: math.MaxUint64, ShardID: 1, HeaderHash: []byte("hash2")},
+			},
+		}
+
+		err := mdr.RequestMissingShardHeaders(metaHeader)
+		require.Nil(t, err)
+
+		time.Sleep(50 * time.Millisecond)
+
+		mut.Lock()
+		require.Equal(t, 0, nonceRequestCount)
+		mut.Unlock()
+	})
+
+	t.Run("valid gap within bounds should trigger correct nonce gap requests", func(t *testing.T) {
+		t.Parallel()
+
+		requestedNonces := make(map[uint32][]uint64)
+		mut := sync.Mutex{}
+
+		headersPool := &pool.HeadersPoolStub{
+			GetHeaderByHashCalled: func(_ []byte) (data.HeaderHandler, error) {
+				return nil, headerNotFoundErr
+			},
+			GetHeaderByNonceAndShardIdCalled: func(_ uint64, _ uint32) ([]data.HeaderHandler, [][]byte, error) {
+				return nil, nil, headerNotFoundErr
+			},
+		}
+		proofsPool := &dataRetriever.ProofsPoolMock{
+			HasProofCalled: func(_ uint32, _ []byte) bool { return false },
+			GetProofByNonceCalled: func(_ uint64, _ uint32) (data.HeaderProofHandler, error) {
+				return nil, headerNotFoundErr
+			},
+		}
+		requestHandler := &testscommon.RequestHandlerStub{
+			RequestShardHeaderCalled:           func(_ uint32, _ []byte) {},
+			RequestEquivalentProofByHashCalled: func(_ uint32, _ []byte) {},
+			RequestShardHeaderByNonceCalled: func(shardID uint32, nonce uint64) {
+				mut.Lock()
+				requestedNonces[shardID] = append(requestedNonces[shardID], nonce)
+				mut.Unlock()
+			},
+			RequestEquivalentProofByNonceCalled: func(_ uint32, _ uint64) {},
+		}
+		blockDataRequester := &preprocMocks.BlockDataRequesterStub{}
+		args := ResolverArgs{
+			HeadersPool:        headersPool,
+			ProofsPool:         proofsPool,
+			RequestHandler:     requestHandler,
+			BlockDataRequester: blockDataRequester,
+		}
+		mdr, _ := NewMissingDataResolver(args)
+
+		// finalized=10, proposed=15: gap=5, should request nonces 11,12,13,14
+		metaHeader := &block.MetaBlockV3{
+			ShardInfoProposal: []block.ShardDataProposal{
+				{Nonce: 15, ShardID: 1, HeaderHash: []byte("hash1")},
+			},
+			ShardInfo: []block.ShardData{
+				{Nonce: 10, ShardID: 1, HeaderHash: []byte("hash2")},
+			},
+		}
+
+		err := mdr.RequestMissingShardHeaders(metaHeader)
+		require.Nil(t, err)
+
+		time.Sleep(50 * time.Millisecond)
+
+		mut.Lock()
+		require.ElementsMatch(t, []uint64{11, 12, 13, 14}, requestedNonces[1])
+		mut.Unlock()
+	})
+}
+
 func TestResolver_IsInterfaceNil(t *testing.T) {
 	t.Parallel()
 
```
