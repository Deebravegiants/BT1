# [?] Fix data race in TestLogPoller_Replay (#14431)

## Summary
Severity: Unknown
Chain: Chainlink
Component: smartcontractkit/chainlink
Published: 2024-09-19
Source: https://github.com/smartcontractkit/chainlink/commit/7b324cad8f46ab740ba84c889eca684ed1c87799
Type: security-commit

## Details
Fix data race in TestLogPoller_Replay (#14431)

* Add RWMutex around global head var

* Use atomic.Pointer instead of RWMutex

## Patch
### core/chains/evm/logpoller/log_poller_internal_test.go
```diff
@@ -7,6 +7,7 @@ import (
 	"math/big"
 	"strings"
 	"sync"
+	"sync/atomic"
 	"testing"
 	"time"
 
@@ -287,12 +288,14 @@ func TestLogPoller_Replay(t *testing.T) {
 	db := pgtest.NewSqlxDB(t)
 	orm := NewORM(chainID, db, lggr)
 
-	head := evmtypes.Head{Number: 4}
+	var head atomic.Pointer[evmtypes.Head]
+	head.Store(&evmtypes.Head{Number: 4})
+
 	events := []common.Hash{EmitterABI.Events["Log1"].ID}
 	log1 := types.Log{
 		Index:       0,
 		BlockHash:   common.Hash{},
-		BlockNumber: uint64(head.Number),
+		BlockNumber: uint64(head.Load().Number),
 		Topics:      events,
 		Address:     addr,
 		TxHash:      common.HexToHash("0x1234"),
@@ -301,8 +304,7 @@ func TestLogPoller_Replay(t *testing.T) {
 
 	ec := evmclimocks.NewClient(t)
 	ec.On("HeadByNumber", mock.Anything, mock.Anything).Return(func(context.Context, *big.Int) (*evmtypes.Head, error) {
-		headCopy := head
-		return &headCopy, nil
+		return head.Load(), nil
 	})
 	ec.On("FilterLogs", mock.Anything, mock.Anything).Return([]types.Log{log1}, nil).Once()
 	ec.On("ConfiguredChainID").Return(chainID, nil)
@@ -318,9 +320,9 @@ func TestLogPoller_Replay(t *testing.T) {
 	headTracker := htMocks.NewHeadTracker[*evmtypes.Head, common.Hash](t)
 
 	headTracker.On("LatestAndFinalizedBlock", mock.Anything).Return(func(ctx context.Context) (*evmtypes.Head, *evmtypes.Head, error) {
-		headCopy := head
-		finalized := &evmtypes.Head{Number: headCopy.Number - lpOpts.FinalityDepth}
-		return &headCopy, finalized, nil
+		h := head.Load()
+		finalized := &evmtypes.Head{Number: h.Number - lpOpts.FinalityDepth}
+		return h, finalized, nil
 	})
 	lp := NewLogPoller(orm, ec, lggr, headTracker, lpOpts)
 
@@ -394,7 +396,7 @@ func TestLogPoller_Replay(t *testing.T) {
 		var wg sync.WaitGroup
 		defer func() { wg.Wait() }()
 		ec.On("FilterLogs", mock.Anything, mock.Anything).Once().Return([]types.Log{log1}, nil).Run(func(args mock.Arguments) {
-			head = evmtypes.Head{Number: 4}
+			head.Store(&evmtypes.Head{Number: 4})
 			wg.Add(1)
 			go func() {
 				defer wg.Done()
@@ -421,7 +423,7 @@ func TestLogPoller_Replay(t *testing.T) {
 
 		ec.On("FilterLogs", mock.Anything, mock.Anything).Return([]types.Log{log1}, nil).Maybe() // in case task gets delayed by >= 100ms
 
-		head = evmtypes.Head{Number: 5}
+		head.Store(&evmtypes.Head{Number: 5})
 		t.Cleanup(lp.reset)
 		servicetest.Run(t, lp)
 
@@ -448,7 +450,7 @@ func TestLogPoller_Replay(t *testing.T) {
 			go func() {
 				defer close(done)
 
-				head = evmtypes.Head{Number: 4} // Restore latest block to 4, so this matches the fromBlock requested
+				head.Store(&evmtypes.Head{Number: 4}) // Restore latest block to 4, so this matches the fromBlock requested
 				select {
 				case lp.replayStart <- 4:
 				case <-ctx.Done():
@@ -469,7 +471,7 @@ func TestLogPoller_Replay(t *testing.T) {
 		ec.On("FilterLogs", mock.Anything, mock.Anything).Return([]types.Log{log1}, nil)
 
 		t.Cleanup(lp.reset)
-		head = evmtypes.Head{Number: 5} // Latest block must be > lastProcessed in order for SaveAndPollLogs() to call FilterLogs()
+		head.Store(&evmtypes.Head{Number: 5}) // Latest block must be > lastProcessed in order for SaveAndPollLogs() to call FilterLogs()
 		servicetest.Run(t, lp)
 
 		select {
@@ -482,7 +484,8 @@ func TestLogPoller_Replay(t *testing.T) {
 	// ReplayAsync should return as soon as replayStart is received
 	t.Run("ReplayAsync success", func(t *testing.T) {
 		t.Cleanup(lp.reset)
-		head = evmtypes.Head{Number: 5}
+
+		head.Store(&evmtypes.Head{Number: 5})
 		ec.On("FilterLogs", mock.Anything, mock.Anything).Return([]types.Log{log1}, nil)
 		mockBatchCallContext(t, ec)
 		servicetest.Run(t, lp)
@@ -496,7 +499,7 @@ func TestLogPoller_Replay(t *testing.T) {
 		ctx := testutils.Context(t)
 		t.Cleanup(lp.reset)
 		servicetest.Run(t, lp)
-		head = evmtypes.Head{Number: 4}
+		head.Store(&evmtypes.Head{Number: 4})
 
 		anyErr := pkgerrors.New("async error")
 		observedLogs.TakeAll()
@@ -528,7 +531,8 @@ func TestLogPoller_Replay(t *testing.T) {
 		err := lp.orm.DeleteLogsAndBlocksAfter(ctx, 0)
 		require.NoError(t, err)
 
-		err = lp.orm.InsertBlock(ctx, head.Hash, head.Number, head.Timestamp, head.Number)
+		h := head.Load()
+		err = lp.orm.InsertBlock(ctx, h.Hash, h.Number, h.Timestamp, h.Number)
 		require.NoError(t, err)
 
 		ec.On("FilterLogs", mock.Anything, mock.Anything).Return([]types.Log{log1}, nil)
```
