# [?] fix: prevent nonce gap underflow by validating proposed nonce against finalized nonce

## Summary
Severity: Unknown
Chain: MultiversX
Component: multiversx/mx-chain-go
Published: 2026-02-11
Source: https://github.com/multiversx/mx-chain-go/commit/c3769f3ade99a123c8191c14bde1b519b1ec4224
Type: security-commit

## Details
fix: prevent nonce gap underflow by validating proposed nonce against finalized nonce

## Patch
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
