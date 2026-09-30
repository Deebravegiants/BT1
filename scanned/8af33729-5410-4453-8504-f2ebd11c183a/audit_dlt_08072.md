# [?] core: fix panic when stat-ing a tx from a queue-only account (#15714)

## Summary
Severity: Unknown
Chain: Celo
Component: celo-org/celo-blockchain
Published: 2017-12-20
Source: https://github.com/celo-org/celo-blockchain/commit/5e1581c2c3a88754f5f492b8551a96c2f5d4664a
Type: security-commit

## Details
core: fix panic when stat-ing a tx from a queue-only account (#15714)

## Patch
### core/tx_pool.go
```diff
@@ -838,7 +838,7 @@ func (pool *TxPool) Status(hashes []common.Hash) []TxStatus {
 	for i, hash := range hashes {
 		if tx := pool.all[hash]; tx != nil {
 			from, _ := types.Sender(pool.signer, tx) // already validated
-			if pool.pending[from].txs.items[tx.Nonce()] != nil {
+			if pool.pending[from] != nil && pool.pending[from].txs.items[tx.Nonce()] != nil {
 				status[i] = TxStatusPending
 			} else {
 				status[i] = TxStatusQueued
```

### core/tx_pool_test.go
```diff
@@ -1563,6 +1563,63 @@ func testTransactionJournaling(t *testing.T, nolocals bool) {
 	pool.Stop()
 }
 
+// TestTransactionStatusCheck tests that the pool can correctly retrieve the
+// pending status of individual transactions.
+func TestTransactionStatusCheck(t *testing.T) {
+	t.Parallel()
+
+	// Create the pool to test the status retrievals with
+	db, _ := ethdb.NewMemDatabase()
+	statedb, _ := state.New(common.Hash{}, state.NewDatabase(db))
+	blockchain := &testBlockChain{statedb, big.NewInt(1000000), new(event.Feed)}
+
+	pool := NewTxPool(testTxPoolConfig, params.TestChainConfig, blockchain)
+	defer pool.Stop()
+
+	// Create the test accounts to check various transaction statuses with
+	keys := make([]*ecdsa.PrivateKey, 3)
+	for i := 0; i < len(keys); i++ {
+		keys[i], _ = crypto.GenerateKey()
+		pool.currentState.AddBalance(crypto.PubkeyToAddress(keys[i].PublicKey), big.NewInt(1000000))
+	}
+	// Generate and queue a batch of transactions, both pending and queued
+	txs := types.Transactions{}
+
+	txs = append(txs, pricedTransaction(0, big.NewInt(100000), big.NewInt(1), keys[0])) // Pending only
+	txs = append(txs, pricedTransaction(0, big.NewInt(100000), big.NewInt(1), keys[1])) // Pending and queued
+	txs = append(txs, pricedTransaction(2, big.NewInt(100000), big.NewInt(1), keys[1]))
+	txs = append(txs, pricedTransaction(2, big.NewInt(100000), big.NewInt(1), keys[2])) // Queued only
+
+	// Import the transaction and ensure they are correctly added
+	pool.AddRemotes(txs)
+
+	pending, queued := pool.Stats()
+	if pending != 2 {
+		t.Fatalf("pending transactions mismatched: have %d, want %d", pending, 2)
+	}
+	if queued != 2 {
+		t.Fatalf("queued transactions mismatched: have %d, want %d", queued, 2)
+	}
+	if err := validateTxPoolInternals(pool); err != nil {
+		t.Fatalf("pool internal state corrupted: %v", err)
+	}
+	// Retrieve the status of each transaction and validate them
+	hashes := make([]common.Hash, len(txs))
+	for i, tx := range txs {
+		hashes[i] = tx.Hash()
+	}
+	hashes = append(hashes, common.Hash{})
+
+	statuses := pool.Status(hashes)
+	expect := []TxStatus{TxStatusPending, TxStatusPending, TxStatusQueued, TxStatusQueued, TxStatusUnknown}
+
+	for i := 0; i < len(statuses); i++ {
+		if statuses[i] != expect[i] {
+			t.Errorf("transaction %d: status mismatch: have %v, want %v", i, statuses[i], expect[i])
+		}
+	}
+}
+
 // Benchmarks the speed of validating the contents of the pending queue of the
 // transaction pool.
 func BenchmarkPendingDemotion100(b *testing.B)   { benchmarkPendingDemotion(b, 100) }
```
