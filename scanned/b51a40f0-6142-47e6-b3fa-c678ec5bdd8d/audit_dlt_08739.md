# [?] fix(worker): prioritize overflow tx as first tx in next block (#563)

## Summary
Severity: Unknown
Chain: Scroll
Component: scroll-tech/go-ethereum
Published: 2023-11-14
Source: https://github.com/scroll-tech/go-ethereum/commit/3f9b23d33e9663f1c02fd546372126a2975b994c
Type: security-commit

## Details
fix(worker): prioritize overflow tx as first tx in next block (#563)

* fix(worker): prioritize overflow tx as first tx in next block

* add tests

* bump version

## Patch
### miner/worker.go
```diff
@@ -155,6 +155,13 @@ type intervalAdjust struct {
 	inc   bool
 }
 
+// prioritizedTransaction represents a single transaction that
+// should be processed as the first transaction in the next block.
+type prioritizedTransaction struct {
+	blockNumber uint64
+	tx          *types.Transaction
+}
+
 // worker is the main object which takes care of submitting new work to consensus engine
 // and gathering the sealing result.
 type worker struct {
@@ -222,6 +229,7 @@ type worker struct {
 	isLocalBlock func(block *types.Block) bool // Function used to determine whether the specified block is mined by local miner.
 
 	circuitCapacityChecker *circuitcapacitychecker.CircuitCapacityChecker
+	prioritizedTx          *prioritizedTransaction
 
 	// Test hooks
 	newTaskHook  func(*task)                        // Method to call upon receiving a new sealing task.
@@ -1136,6 +1144,17 @@ loop:
 				// but it's a trade-off between tracing overhead & block usage rate
 				log.Trace("Circuit capacity limit reached in a block", "acc_rows", w.current.accRows, "tx", tx.Hash().String())
 				log.Info("Skipping message", "tx", tx.Hash().String(), "block", w.current.header.Number, "reason", "accumulated row consumption overflow")
+
+				// Prioritize transaction for the next block.
+				// If there are no new L1 messages, this transaction will be the 1st transaction in the next block,
+				// at which point we can definitively decide if we should skip it or not.
+				log.Debug("Prioritizing transaction for next block", "blockNumber", w.current.header.Number.Uint64()+1, "tx", tx.Hash().String())
+				w.prioritizedTx = &prioritizedTransaction{
+					blockNumber: w.current.header.Number.Uint64() + 1,
+					tx:          tx,
+				}
+				atomic.AddInt32(&w.newTxs, int32(1))
+
 				circuitCapacityReached = true
 				break loop
 			} else {
@@ -1415,6 +1434,19 @@ func (w *worker) commitNewWork(interrupt *int32, noempty bool, timestamp int64)
 			return
 		}
 	}
+	if w.prioritizedTx != nil && w.current.header.Number.Uint64() > w.prioritizedTx.blockNumber {
+		w.prioritizedTx = nil
+	}
+	if !circuitCapacityReached && w.prioritizedTx != nil && w.current.header.Number.Uint64() == w.prioritizedTx.blockNumber {
+		tx := w.prioritizedTx.tx
+		from, _ := types.Sender(w.current.signer, tx) // error already checked before
+		txList := map[common.Address]types.Transactions{from: []*types.Transaction{tx}}
+		txs := types.NewTransactionsByPriceAndNonce(w.current.signer, txList, header.BaseFee)
+		skipCommit, circuitCapacityReached = w.commitTransactions(txs, w.coinbase, interrupt)
+		if skipCommit {
+			return
+		}
+	}
 	if len(localTxs) > 0 && !circuitCapacityReached {
 		txs := types.NewTransactionsByPriceAndNonce(w.current.signer, localTxs, header.BaseFee)
 		skipCommit, circuitCapacityReached = w.commitTransactions(txs, w.coinbase, interrupt)
```

### miner/worker_test.go
```diff
@@ -1115,6 +1115,85 @@ func TestOversizedTxThenNormal(t *testing.T) {
 	})
 }
 
+func TestPrioritizeOverflowTx(t *testing.T) {
+	assert := assert.New(t)
+
+	var (
+		chainConfig = params.AllCliqueProtocolChanges
+		db          = rawdb.NewMemoryDatabase()
+		engine      = clique.New(chainConfig.Clique, db)
+	)
+
+	chainConfig.Clique = &params.CliqueConfig{Period: 1, Epoch: 30000}
+	chainConfig.LondonBlock = big.NewInt(0)
+
+	w, b := newTestWorker(t, chainConfig, engine, db, 0)
+	defer w.close()
+
+	// This test chain imports the mined blocks.
+	db2 := rawdb.NewMemoryDatabase()
+	b.genesis.MustCommit(db2)
+	chain, _ := core.NewBlockChain(db2, nil, b.chain.Config(), engine, vm.Config{
+		Debug:  true,
+		Tracer: vm.NewStructLogger(&vm.LogConfig{EnableMemory: true, EnableReturnData: true})}, nil, nil, false)
+	defer chain.Stop()
+
+	// Ignore empty commit here for less noise.
+	w.skipSealHook = func(task *task) bool {
+		return len(task.receipts) == 0
+	}
+
+	// Wait for mined blocks.
+	sub := w.mux.Subscribe(core.NewMinedBlockEvent{})
+	defer sub.Unsubscribe()
+
+	// Define 3 transactions:
+	// A --> B (nonce: 0, gas: 20)
+	tx0, _ := types.SignTx(types.NewTransaction(b.txPool.Nonce(testBankAddress), testUserAddress, big.NewInt(100000000000000000), params.TxGas, big.NewInt(20*params.InitialBaseFee), nil), types.HomesteadSigner{}, testBankKey)
+	// A --> B (nonce: 1, gas: 5)
+	tx1, _ := types.SignTx(types.NewTransaction(b.txPool.Nonce(testBankAddress)+1, testUserAddress, big.NewInt(0), params.TxGas, big.NewInt(5*params.InitialBaseFee), nil), types.HomesteadSigner{}, testBankKey)
+	// B --> A (nonce: 0, gas: 20)
+	tx2, _ := types.SignTx(types.NewTransaction(b.txPool.Nonce(testUserAddress), testBankAddress, big.NewInt(0), params.TxGas, big.NewInt(20*params.InitialBaseFee), nil), types.HomesteadSigner{}, testUserKey)
+
+	// Process 2 transactions with gas order: tx0 > tx1, tx1 will overflow.
+	b.txPool.AddRemotesSync([]*types.Transaction{tx0, tx1})
+	w.getCCC().ScheduleError(2, circuitcapacitychecker.ErrBlockRowConsumptionOverflow)
+	w.start()
+
+	select {
+	case ev := <-sub.Chan():
+		w.stop()
+		block := ev.Data.(core.NewMinedBlockEvent).Block
+		assert.Equal(1, len(block.Transactions()))
+		assert.Equal(tx0.Hash(), block.Transactions()[0].Hash())
+		if _, err := chain.InsertChain([]*types.Block{block}); err != nil {
+			t.Fatalf("failed to insert new mined block %d: %v", block.NumberU64(), err)
+		}
+	case <-time.After(3 * time.Second): // Worker needs 1s to include new changes.
+		t.Fatalf("timeout")
+	}
+
+	// Process 2 transactions with gas order: tx2 > tx1,
+	// but we will prioritize tx1.
+	b.txPool.AddRemotesSync([]*types.Transaction{tx2})
+	w.start()
+
+	select {
+	case ev := <-sub.Chan():
+		w.stop()
+		block := ev.Data.(core.NewMinedBlockEvent).Block
+		assert.Equal(2, len(block.Transactions()))
+		// note: txs are not included according to their gas fee order
+		assert.Equal(tx1.Hash(), block.Transactions()[0].Hash())
+		assert.Equal(tx2.Hash(), block.Transactions()[1].Hash())
+		if _, err := chain.InsertChain([]*types.Block{block}); err != nil {
+			t.Fatalf("failed to insert new mined block %d: %v", block.NumberU64(), err)
+		}
+	case <-time.After(3 * time.Second): // Worker needs 1s to include new changes.
+		t.Fatalf("timeout")
+	}
+}
+
 func TestSkippedTransactionDatabaseEntries(t *testing.T) {
 	assert := assert.New(t)
 
```

### params/version.go
```diff
@@ -24,7 +24,7 @@ import (
 const (
 	VersionMajor = 5         // Major version component of the current release
 	VersionMinor = 1         // Minor version component of the current release
-	VersionPatch = 2         // Patch version component of the current release
+	VersionPatch = 3         // Patch version component of the current release
 	VersionMeta  = "mainnet" // Version metadata to append to the version string
 )
 
```
