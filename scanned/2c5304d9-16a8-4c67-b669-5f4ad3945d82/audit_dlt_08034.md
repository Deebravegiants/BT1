# [?] miner: fix data race in tests (#20310)

## Summary
Severity: Unknown
Chain: Celo
Component: celo-org/celo-blockchain
Published: 2019-11-20
Source: https://github.com/celo-org/celo-blockchain/commit/9b59c75405282d5628d4f416160b8984cd76a168
Type: security-commit

## Details
miner: fix data race in tests (#20310)

* miner: fix data race in tests

miner: fix linter

* miner: address comment

## Patch
### miner/miner.go
```diff
@@ -72,7 +72,7 @@ func New(eth Backend, config *Config, chainConfig *params.ChainConfig, mux *even
 		mux:      mux,
 		engine:   engine,
 		exitCh:   make(chan struct{}),
-		worker:   newWorker(config, chainConfig, engine, eth, mux, isLocalBlock),
+		worker:   newWorker(config, chainConfig, engine, eth, mux, isLocalBlock, true),
 		canStart: 1,
 	}
 	go miner.update()
```

### miner/worker.go
```diff
@@ -176,7 +176,7 @@ type worker struct {
 	resubmitHook func(time.Duration, time.Duration) // Method to call upon updating resubmitting interval.
 }
 
-func newWorker(config *Config, chainConfig *params.ChainConfig, engine consensus.Engine, eth Backend, mux *event.TypeMux, isLocalBlock func(*types.Block) bool) *worker {
+func newWorker(config *Config, chainConfig *params.ChainConfig, engine consensus.Engine, eth Backend, mux *event.TypeMux, isLocalBlock func(*types.Block) bool, init bool) *worker {
 	worker := &worker{
 		config:             config,
 		chainConfig:        chainConfig,
@@ -219,8 +219,9 @@ func newWorker(config *Config, chainConfig *params.ChainConfig, engine consensus
 	go worker.taskLoop()
 
 	// Submit first work to initialize pending state.
-	worker.startCh <- struct{}{}
-
+	if init {
+		worker.startCh <- struct{}{}
+	}
 	return worker
 }
 
```

### miner/worker_test.go
```diff
@@ -19,6 +19,7 @@ package miner
 import (
 	"math/big"
 	"math/rand"
+	"sync/atomic"
 	"testing"
 	"time"
 
@@ -180,7 +181,7 @@ func (b *testWorkerBackend) newRandomTx(creation bool) *types.Transaction {
 func newTestWorker(t *testing.T, chainConfig *params.ChainConfig, engine consensus.Engine, db ethdb.Database, blocks int) (*worker, *testWorkerBackend) {
 	backend := newTestWorkerBackend(t, chainConfig, engine, db, blocks)
 	backend.txPool.AddLocals(pendingTxs)
-	w := newWorker(testConfig, chainConfig, engine, backend, new(event.TypeMux), nil)
+	w := newWorker(testConfig, chainConfig, engine, backend, new(event.TypeMux), nil, false)
 	w.setEtherbase(testBankAddress)
 	return w, backend
 }
@@ -230,32 +231,13 @@ func testGenerateBlockAndImport(t *testing.T, isClique bool) {
 			newBlock <- struct{}{}
 		}
 	}
-
-	// Ensure worker has finished initialization
-	for {
-		b := w.pendingBlock()
-		if b != nil && b.NumberU64() == 1 {
-			break
-		}
-	}
-	w.start() // Start mining!
-
-	// Ignore first 2 commits caused by start operation
-	ignored := make(chan struct{}, 2)
-	w.skipSealHook = func(task *task) bool {
-		ignored <- struct{}{}
-		return true
-	}
-	for i := 0; i < 2; i++ {
-		<-ignored
-	}
-
-	go listenNewBlock()
-
 	// Ignore empty commit here for less noise
 	w.skipSealHook = func(task *task) bool {
 		return len(task.receipts) == 0
 	}
+	w.start() // Start mining!
+	go listenNewBlock()
+
 	for i := 0; i < 5; i++ {
 		b.txPool.AddLocal(b.newRandomTx(true))
 		b.txPool.AddLocal(b.newRandomTx(false))
@@ -269,38 +251,6 @@ func testGenerateBlockAndImport(t *testing.T, isClique bool) {
 	}
 }
 
-func TestPendingStateAndBlockEthash(t *testing.T) {
-	testPendingStateAndBlock(t, ethashChainConfig, ethash.NewFaker())
-}
-func TestPendingStateAndBlockClique(t *testing.T) {
-	testPendingStateAndBlock(t, cliqueChainConfig, clique.New(cliqueChainConfig.Clique, rawdb.NewMemoryDatabase()))
-}
-
-func testPendingStateAndBlock(t *testing.T, chainConfig *params.ChainConfig, engine consensus.Engine) {
-	defer engine.Close()
-
-	w, b := newTestWorker(t, chainConfig, engine, rawdb.NewMemoryDatabase(), 0)
-	defer w.close()
-
-	// Ensure snapshot has been updated.
-	time.Sleep(100 * time.Millisecond)
-	block, state := w.pending()
-	if block.NumberU64() != 1 {
-		t.Errorf("block number mismatch: have %d, want %d", block.NumberU64(), 1)
-	}
-	if balance := state.GetBalance(testUserAddress); balance.Cmp(big.NewInt(1000)) != 0 {
-		t.Errorf("account balance mismatch: have %d, want %d", balance, 1000)
-	}
-	b.txPool.AddLocals(newTxs)
-
-	// Ensure the new tx events has been processed
-	time.Sleep(100 * time.Millisecond)
-	block, state = w.pending()
-	if balance := state.GetBalance(testUserAddress); balance.Cmp(big.NewInt(2000)) != 0 {
-		t.Errorf("account balance mismatch: have %d, want %d", balance, 2000)
-	}
-}
-
 func TestEmptyWorkEthash(t *testing.T) {
 	testEmptyWork(t, ethashChainConfig, ethash.NewFaker())
 }
@@ -315,49 +265,41 @@ func testEmptyWork(t *testing.T, chainConfig *params.ChainConfig, engine consens
 	defer w.close()
 
 	var (
-		taskCh    = make(chan struct{}, 2)
 		taskIndex int
+		taskCh    = make(chan struct{}, 2)
 	)
-
 	checkEqual := func(t *testing.T, task *task, index int) {
+		// The first empty work without any txs included
 		receiptLen, balance := 0, big.NewInt(0)
 		if index == 1 {
+			// The second full work with 1 tx included
 			receiptLen, balance = 1, big.NewInt(1000)
 		}
 		if len(task.receipts) != receiptLen {
-			t.Errorf("receipt number mismatch: have %d, want %d", len(task.receipts), receiptLen)
+			t.Fatalf("receipt number mismatch: have %d, want %d", len(task.receipts), receiptLen)
 		}
 		if task.state.GetBalance(testUserAddress).Cmp(balance) != 0 {
-			t.Errorf("account balance mismatch: have %d, want %d", task.state.GetBalance(testUserAddress), balance)
+			t.Fatalf("account balance mismatch: have %d, want %d", task.state.GetBalance(testUserAddress), balance)
 		}
 	}
-
 	w.newTaskHook = func(task *task) {
 		if task.block.NumberU64() == 1 {
 			checkEqual(t, task, taskIndex)
 			taskIndex += 1
 			taskCh <- struct{}{}
 		}
 	}
+	w.skipSealHook = func(task *task) bool { return true }
 	w.fullTaskHook = func() {
 		// Aarch64 unit tests are running in a VM on travis, they must
 		// be given more time to execute.
 		time.Sleep(time.Second)
 	}
-
-	// Ensure worker has finished initialization
-	for {
-		b := w.pendingBlock()
-		if b != nil && b.NumberU64() == 1 {
-			break
-		}
-	}
-
-	w.start()
+	w.start() // Start mining!
 	for i := 0; i < 2; i += 1 {
 		select {
 		case <-taskCh:
-		case <-time.NewTimer(30 * time.Second).C:
+		case <-time.NewTimer(3 * time.Second).C:
 			t.Error("new task timeout")
 		}
 	}
@@ -375,6 +317,9 @@ func TestStreamUncleBlock(t *testing.T) {
 	taskIndex := 0
 	w.newTaskHook = func(task *task) {
 		if task.block.NumberU64() == 2 {
+			// The first task is an empty task, the second
+			// one has 1 pending tx, the third one has 1 tx
+			// and 1 uncle.
 			if taskIndex == 2 {
 				have := task.block.Header().UncleHash
 				want := types.CalcUncleHash([]*types.Header{b.uncleBlock.Header()})
@@ -392,26 +337,17 @@ func TestStreamUncleBlock(t *testing.T) {
 	w.fullTaskHook = func() {
 		time.Sleep(100 * time.Millisecond)
 	}
-
-	// Ensure worker has finished initialization
-	for {
-		b := w.pendingBlock()
-		if b != nil && b.NumberU64() == 2 {
-			break
-		}
-	}
 	w.start()
 
-	// Ignore the first two works
 	for i := 0; i < 2; i += 1 {
 		select {
 		case <-taskCh:
 		case <-time.NewTimer(time.Second).C:
 			t.Error("new task timeout")
 		}
 	}
-	b.PostChainEvents([]interface{}{core.ChainSideEvent{Block: b.uncleBlock}})
 
+	b.PostChainEvents([]interface{}{core.ChainSideEvent{Block: b.uncleBlock}})
 	select {
 	case <-taskCh:
 	case <-time.NewTimer(time.Second).C:
@@ -438,6 +374,8 @@ func testRegenerateMiningBlock(t *testing.T, chainConfig *params.ChainConfig, en
 	taskIndex := 0
 	w.newTaskHook = func(task *task) {
 		if task.block.NumberU64() == 1 {
+			// The first task is an empty task, the second
+			// one has 1 pending tx, the third one has 2 txs
 			if taskIndex == 2 {
 				receiptLen, balance := 2, big.NewInt(2000)
 				if len(task.receipts) != receiptLen {
@@ -457,13 +395,6 @@ func testRegenerateMiningBlock(t *testing.T, chainConfig *params.ChainConfig, en
 	w.fullTaskHook = func() {
 		time.Sleep(100 * time.Millisecond)
 	}
-	// Ensure worker has finished initialization
-	for {
-		b := w.pendingBlock()
-		if b != nil && b.NumberU64() == 1 {
-			break
-		}
-	}
 
 	w.start()
 	// Ignore the first two works
@@ -508,11 +439,11 @@ func testAdjustInterval(t *testing.T, chainConfig *params.ChainConfig, engine co
 		progress = make(chan struct{}, 10)
 		result   = make([]float64, 0, 10)
 		index    = 0
-		start    = false
+		start    uint32
 	)
 	w.resubmitHook = func(minInterval time.Duration, recommitInterval time.Duration) {
 		// Short circuit if interval checking hasn't started.
-		if !start {
+		if atomic.LoadUint32(&start) == 0 {
 			return
 		}
 		var wantMinInterval, wantRecommitInterval time.Duration
@@ -544,19 +475,11 @@ func testAdjustInterval(t *testing.T, chainConfig *params.ChainConfig, engine co
 		index += 1
 		progress <- struct{}{}
 	}
-	// Ensure worker has finished initialization
-	for {
-		b := w.pendingBlock()
-		if b != nil && b.NumberU64() == 1 {
-			break
-		}
-	}
-
 	w.start()
 
-	time.Sleep(time.Second)
+	time.Sleep(time.Second) // Ensure two tasks have been summitted due to start opt
+	atomic.StoreUint32(&start, 1)
 
-	start = true
 	w.setRecommitInterval(3 * time.Second)
 	select {
 	case <-progress:
```
