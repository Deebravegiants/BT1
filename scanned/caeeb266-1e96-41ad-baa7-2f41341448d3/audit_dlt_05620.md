# [?] [SharovBot] execution/execmodule: fix DATA RACE on miningCancel channel teardown (#22842)

## Summary
Severity: Unknown
Chain: Ethereum
Component: erigontech/erigon
Published: 2026-07-29
Source: https://github.com/erigontech/erigon/commit/d532725c6bf25345c9470abf156542df9b182920
Type: security-commit

## Details
[SharovBot] execution/execmodule: fix DATA RACE on miningCancel channel teardown (#22842)

**[SharovBot]**

## Summary

Fix a DATA RACE detected in
`TestGetAssembledBlockHonorsCanceledContextWhenTxPoolIsBehindParent`.

## Root Cause

The `miningCancel` channel in `execmoduletester.New` was:
1. **Sent to** (non-blocking) by `builder.finishBlock` at
`finish.go:124` — to cancel an in-flight sealing task
2. **Closed** by a teardown goroutine when `mock.Ctx` is cancelled

A concurrent `close(ch)` + `ch <- v` on the same channel is a DATA RACE
(detected by Go's race detector as a `closechan` write racing with a
`chansend` read).

## Fix

Change `miningCancel` from an unbuffered channel that gets closed to a
**buffered channel (capacity 1)** that receives a non-blocking send on
shutdown. This eliminates the close-while-send race without changing
observable semantics:

- `finishBlock` already uses a non-blocking `select` when sending to
`sealCancel`
- No active sealer (`Merge`, `FakeEthash`) actually receives from the
`stop` channel passed to `engine.Seal()`
- The buffered capacity ensures the shutdown signal is not dropped if no
goroutine is listening at the moment of the send

## Testing

```
go test -race -count=3 -run TestGetAssembledBlockHonorsCanceledContextWhenTxPoolIsBehindParent ./execution/execmodule/...
```

Passes with no DATA RACE warnings (3 consecutive runs).

CI failure:
https://github.com/erigontech/erigon/actions/runs/30418424459/job/90469879338

---------

Co-authored-by: SharovBot <erigon-ci@erigon.tech>
Co-authored-by: Giulio Rebuffo <giulio.rebuffo@gmail.com>
Co-authored-by: Alexey Sharov <askalexsharov@gmail.com>

### execution/execmodule/execmoduletester/exec_module_tester.go
```diff
@@ -672,11 +672,8 @@ func New(tb testing.TB, opts ...Option) *ExecModuleTester {
 
 	snapDownloader := mockDownloader(ctrl, mock.Dirs.Snap)
 
-	miningCancel := make(chan struct{})
-	go func() {
-		<-mock.Ctx.Done()
-		close(miningCancel)
-	}()
+	// Never closed: finishBlock sends to it concurrently to abort an in-flight seal.
+	sealCancel := make(chan struct{})
 
 	readAheader := exec.NewBlockReadAheader()
 	blkBuilder := builder.NewBuilder(
@@ -707,7 +704,7 @@ func New(tb testing.TB, opts ...Option) *ExecModuleTester {
 		&vm.Config{},
 		dirs.Tmp,
 		mock.TxPool,
-		miningCancel,
+		sealCancel,
 		latestBlockBuiltStore,
 		nil, /*sdProvider*/
 		logger,
```

### node/eth/backend.go
```diff
@@ -166,7 +166,7 @@ type Ethereum struct {
 	rpcDaemonStateCache kvcache.Cache
 	mcpRPC              *mcp.ErigonMCPServer
 
-	miningSealingQuit   chan struct{}
+	sealCancel          chan struct{}
 	pendingBlocks       chan *types.Block
 	minedBlocks         chan *types.Block
 	minedBlockObservers *event.Observers[*types.Block]
@@ -338,7 +338,7 @@ func New(ctx context.Context, stack *node.Node, config *ethconfig.Config, logger
 		networkID:                 config.NetworkID,
 		etherbase:                 config.Builder.Etherbase,
 		blockBuilderNotifyNewTxns: make(chan struct{}, 1),
-		miningSealingQuit:         make(chan struct{}),
+		sealCancel:                make(chan struct{}),
 		minedBlocks:               make(chan *types.Block, 1),
 		minedBlockObservers:       event.NewObservers[*types.Block](),
 		logger:                    logger,
@@ -836,7 +836,7 @@ func New(ctx context.Context, stack *node.Node, config *ethconfig.Config, logger
 		&vm.Config{},
 		tmpdir,
 		txnProvider,
-		backend.miningSealingQuit,
+		backend.sealCancel,
 		latestBlockBuiltStore,
 		backend.notifications.Events.LatestSD,
 		logger,
```
