# [?] execution: fix GetAssembledBlock deadlock (#22835)

## Summary
Severity: Unknown
Chain: Ethereum
Component: erigontech/erigon
Published: 2026-07-29
Source: https://github.com/erigontech/erigon/commit/8cc9d5271800307d7386450acc5b1b745144459a
Type: security-commit

## Details
execution: fix GetAssembledBlock deadlock (#22835)

fixes https://github.com/erigontech/erigon/issues/22631

## Summary

- Make `BlockBuilder.Stop` wait for either builder completion or
cancellation of the caller's context.
- Propagate the `GetAssembledBlock` request context into the builder
wait.
- Add a regression test using the real txpool with `lastSeenBlock`
behind the builder's parent.

## Root cause

During a rapid reorg, an asynchronous payload builder could remain based
on block N after the txpool had unwound to N-1. The builder then waited
in `TxPool.best` for the txpool to reach N.

When the consensus client subsequently requested that payload,
`GetAssembledBlock` ignored request cancellation and waited indefinitely
in `BlockBuilder.Stop`. This retained the execution semaphore and the
Engine API's outer lock, preventing later `newPayload` and
`forkchoiceUpdated` requests from advancing execution and notifying the
txpool. The resulting circular wait could wedge stateful Engine API
traffic indefinitely.

## Change

Replace the builder's completion condition variable with a completion
channel while continuing to protect its result with a mutex.
`BlockBuilder.Stop` now selects between that completion channel and
`ctx.Done()`.

When a payload request is canceled or reaches its deadline,
`GetAssembledBlock` returns the context error and releases the execution
semaphore. This allows the Engine API handler to unwind and newer
stateful requests to proceed. Normal completed-builder behavior remains
unchanged.

### execution/builder/block_builder.go
```diff
@@ -17,6 +17,7 @@
 package builder
 
 import (
+	"context"
 	"fmt"
 	"sync"
 	"sync/atomic"
@@ -32,18 +33,16 @@ type BlockBuilderFunc func(param *Parameters, interrupt *atomic.Bool) (*types.Bl
 // BlockBuilder wraps a goroutine that builds Proof-of-Stake payloads (PoS "mining")
 type BlockBuilder struct {
 	interrupt atomic.Bool
-	syncCond  *sync.Cond
+	mu        sync.Mutex
+	done      chan struct{}
 	result    *types.BlockWithReceipts
 	err       error
 }
 
 func NewBlockBuilder(build BlockBuilderFunc, param *Parameters, maxBuildTimeSecs uint64) *BlockBuilder {
-	builder := new(BlockBuilder)
-	builder.syncCond = sync.NewCond(new(sync.Mutex))
-	terminated := make(chan struct{})
+	builder := &BlockBuilder{done: make(chan struct{})}
 
 	go func() {
-		defer close(terminated)
 		var result *types.BlockWithReceipts
 		var err error
 
@@ -54,11 +53,11 @@ func NewBlockBuilder(build BlockBuilderFunc, param *Parameters, maxBuildTimeSecs
 				result = nil
 			}
 
-			builder.syncCond.L.Lock()
-			defer builder.syncCond.L.Unlock()
+			builder.mu.Lock()
 			builder.result = result
 			builder.err = err
-			builder.syncCond.Broadcast()
+			builder.mu.Unlock()
+			close(builder.done)
 		}()
 
 		log.Info("Building block...")
@@ -78,32 +77,34 @@ func NewBlockBuilder(build BlockBuilderFunc, param *Parameters, maxBuildTimeSecs
 		select {
 		case <-timer.C:
 			log.Warn("Stopping block builder due to max build time exceeded")
-			_, _ = builder.Stop()
+			_, _ = builder.Stop(context.Background())
 			log.Debug("Stopped block builder due to max build time exceeded")
 			return
-		case <-terminated:
+		case <-builder.done:
 			return
 		}
 	}()
 
 	return builder
 }
 
-func (b *BlockBuilder) Stop() (*types.BlockWithReceipts, error) {
+func (b *BlockBuilder) Stop(ctx context.Context) (*types.BlockWithReceipts, error) {
 	b.interrupt.Store(true)
 
-	b.syncCond.L.Lock()
-	defer b.syncCond.L.Unlock()
-	for b.result == nil && b.err == nil {
-		b.syncCond.Wait()
+	select {
+	case <-ctx.Done():
+		return nil, ctx.Err()
+	case <-b.done:
 	}
 
+	b.mu.Lock()
+	defer b.mu.Unlock()
 	return b.result, b.err
 }
 
 func (b *BlockBuilder) Block() *types.Block {
-	b.syncCond.L.Lock()
-	defer b.syncCond.L.Unlock()
+	b.mu.Lock()
+	defer b.mu.Unlock()
 
 	if b.result == nil {
 		return nil
```

### execution/execmodule/block_building.go
```diff
@@ -96,7 +96,7 @@ func blockValue(br *types.BlockWithReceipts, baseFee *uint256.Int) *uint256.Int
 	return blockValue
 }
 
-func (e *ExecModule) GetAssembledBlock(_ context.Context, payloadID uint64) (AssembledBlockResult, error) {
+func (e *ExecModule) GetAssembledBlock(ctx context.Context, payloadID uint64) (AssembledBlockResult, error) {
 	if !e.semaphore.TryAcquire(1) {
 		return AssembledBlockResult{Busy: true}, nil
 	}
@@ -106,7 +106,7 @@ func (e *ExecModule) GetAssembledBlock(_ context.Context, payloadID uint64) (Ass
 	if !ok {
 		return AssembledBlockResult{}, nil
 	}
-	blockWithReceipts, err := bldr.Stop()
+	blockWithReceipts, err := bldr.Stop(ctx)
 	if err != nil {
 		e.logger.Error("Failed to build PoS block", "err", err)
 		return AssembledBlockResult{}, err
```

### execution/execmodule/exec_module_test.go
```diff
@@ -59,8 +59,10 @@ import (
 	"github.com/erigontech/erigon/execution/tests/blockgen"
 	"github.com/erigontech/erigon/execution/types"
 	"github.com/erigontech/erigon/execution/types/accounts"
+	"github.com/erigontech/erigon/node/gointerfaces/remoteproto"
 	"github.com/erigontech/erigon/node/gointerfaces/txpoolproto"
 	"github.com/erigontech/erigon/txnprovider"
+	txnpool "github.com/erigontech/erigon/txnprovider/txpool"
 )
 
 type blockingTxnProvider struct {
@@ -90,6 +92,35 @@ func (p *blockingTxnProvider) ProvideTxns(ctx context.Context, _ ...txnprovider.
 	return nil, nil
 }
 
+type rewindingTxnProvider struct {
+	pool  *txnpool.TxPool
+	head  *remoteproto.StateChangeBatch
+	ready chan struct{}
+	once  sync.Once
+	err   error
+}
+
+func (p *rewindingTxnProvider) ProvideTxns(ctx context.Context, opts ...txnprovider.ProvideOption) ([]types.Transaction, error) {
+	p.once.Do(func() {
+		p.err = p.pool.OnNewBlock(ctx, p.head, txnpool.TxnSlots{}, txnpool.TxnSlots{}, txnpool.TxnSlots{})
+		close(p.ready)
+	})
+	if p.err != nil {
+		return nil, p.err
+	}
+	return p.pool.ProvideTxns(ctx, opts...)
+}
+
+func txPoolHead(block *types.Block) *remoteproto.StateChangeBatch {
+	return &remoteproto.StateChangeBatch{
+		PendingBlockBaseFee: block.BaseFee().Uint64(),
+		BlockGasLimit:       block.GasLimit(),
+		ChangeBatch: []*remoteproto.StateChange{
+			{BlockHeight: block.NumberU64()},
+		},
+	}
+}
+
 func TestValidateChainWithLastTxNumOfBlockAtStepBoundary(t *testing.T) {
 	// See https://github.com/erigontech/erigon/issues/18823
 	ctx := t.Context()
@@ -682,6 +713,65 @@ func TestAssembleBlockWithConcurrentSiblingCommit(t *testing.T) {
 	require.Equal(t, execmodule.ExecutionStatusSuccess, validation.ValidationStatus)
 }
 
+func TestGetAssembledBlockHonorsCanceledContextWhenTxPoolIsBehindParent(t *testing.T) {
+	ctx := t.Context()
+	m := execmoduletester.New(t, execmoduletester.WithTxPool(), execmoduletester.WithChainConfig(chain.AllProtocolChanges))
+	chainPack, err := blockgen.GenerateChain(m.ChainConfig, m.Genesis, m.Engine, m.DB, 2, nil)
+	require.NoError(t, err)
+	require.NoError(t, m.InsertChain(chainPack))
+
+	parent := chainPack.TopBlock
+	provider := &rewindingTxnProvider{
+		pool:  m.TxPool,
+		head:  txPoolHead(chainPack.Blocks[len(chainPack.Blocks)-2]),
+		ready: make(chan struct{}),
+	}
+	parentBeaconBlockRoot := randomHash()
+	payloadID, err := assembleBlock(ctx, m.ExecModule, &builder.Parameters{
+		ParentHash:            parent.Hash(),
+		Timestamp:             parent.Time() + 1,
+		PrevRandao:            parent.Header().MixDigest,
+		SuggestedFeeRecipient: common.Address{1},
+		Withdrawals:           make([]*types.Withdrawal, 0),
+		ParentBeaconBlockRoot: &parentBeaconBlockRoot,
+		CustomTxnProvider:     provider,
+	})
+	require.NoError(t, err)
+
+	select {
+	case <-provider.ready:
+	case <-time.After(10 * time.Second):
+		t.Fatal("builder did not reach transaction selection")
+	}
+
+	requestCtx, cancel := context.WithCancel(ctx)
+	cancel()
+	resultCh := make(chan error, 1)
+	go func() {
+		_, err := m.ExecModule.GetAssembledBlock(requestCtx, payloadID)
+		resultCh <- err
+	}()
+
+	var requestErr error
+	blocked := false
+	select {
+	case requestErr = <-resultCh:
+	case <-time.After(time.Second):
+		blocked = true
+	}
+
+	require.NoError(t, m.TxPool.OnNewBlock(ctx, txPoolHead(parent), txnpool.TxnSlots{}, txnpool.TxnSlots{}, txnpool.TxnSlots{}))
+	if blocked {
+		select {
+		case <-resultCh:
+		case <-time.After(10 * time.Second):
+			t.Fatal("GetAssembledBlock did not return after restoring the txpool head")
+		}
+		t.Fatal("GetAssembledBlock remained blocked after context cancellation while the txpool was behind the builder parent")
+	}
+	require.ErrorIs(t, requestErr, context.Canceled)
+}
+
 func TestAssembleBlockWithFreshlyAddedTxns(t *testing.T) {
 	if testing.Short() {
 		t.Skip("slow test")
```
