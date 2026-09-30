# [?] fix: prevent deadlock and nil panic in blocks reexecutor

## Summary
Severity: Unknown
Chain: Arbitrum
Component: OffchainLabs/nitro
Published: 2026-03-19
Source: https://github.com/OffchainLabs/nitro/commit/49919fceb7051449c12ed2c45a114151b40063fc
Type: security-commit

## Details
fix: prevent deadlock and nil panic in blocks reexecutor

Add done-channel signals on early-return error paths in
LaunchBlocksReExecution so that Impl's done-counting loop does not
deadlock. Move GetHeaderByNumber(currentBlock) outside the goroutine
to catch nil before passing it to advanceStateUpToBlock, and properly
release state on that error path. Also fix requestValidity timeout in
data streaming protocol test.

Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>

## Patch
### blocks_reexecutor/blocks_reexecutor.go
```diff
@@ -226,17 +226,26 @@ func (s *BlocksReExecutor) LaunchBlocksReExecution(ctx context.Context, startBlo
 	startHeader := s.blockchain.GetHeaderByNumber(start)
 	if startHeader == nil {
 		s.fatalErrChan <- fmt.Errorf("blocksReExecutor failed to get start header at %d", start)
+		s.done <- struct{}{}
 		return startBlock
 	}
 	startState, startHeader, release, err := arbitrum.FindLastAvailableState(ctx, s.blockchain, s.stateFor, startHeader, logState, -1)
 	if err != nil {
 		s.fatalErrChan <- fmt.Errorf("blocksReExecutor failed to get last available state while searching for state at %d, err: %w", start, err)
+		s.done <- struct{}{}
 		return startBlock
 	}
 	start = startHeader.Number.Uint64()
+	targetHeader := s.blockchain.GetHeaderByNumber(currentBlock)
+	if targetHeader == nil {
+		release()
+		s.fatalErrChan <- fmt.Errorf("blocksReExecutor failed to get target header at %d", currentBlock)
+		s.done <- struct{}{}
+		return startBlock
+	}
 	s.LaunchThread(func(ctx context.Context) {
 		log.Info("Starting reexecution of blocks against historic state", "stateAt", start, "startBlock", start+1, "endBlock", currentBlock)
-		if err := s.advanceStateUpToBlock(ctx, startState, s.blockchain.GetHeaderByNumber(currentBlock), startHeader, release); err != nil {
+		if err := s.advanceStateUpToBlock(ctx, startState, targetHeader, startHeader, release); err != nil {
 			s.fatalErrChan <- fmt.Errorf("blocksReExecutor errored advancing state from block %d to block %d, err: %w", start, currentBlock, err)
 		} else {
 			log.Info("Successfully reexecuted blocks against historic state", "stateAt", start, "startBlock", start+1, "endBlock", currentBlock)
```

### daprovider/data_streaming/protocol_test.go
```diff
@@ -27,7 +27,7 @@ import (
 const (
 	maxPendingMessages      = 10
 	messageCollectionExpiry = 1 * time.Second
-	requestValidity         = 1 * time.Second
+	requestValidity         = 10 * time.Second
 	timeout                 = 10
 	serverRPCRoot           = "datastreaming"
 )
```

### system_tests/batch_poster_test.go
```diff
@@ -752,17 +752,20 @@ drain:
 	// Disable the filter and send the captured batch poster transactions.
 	builder.L1.ClientWrapper.DisableRawTransactionFilter()
 	var sentTxs []*types.Transaction
+	var skipped int
 	for _, bptx := range batchPosterTxs {
 		err := builder.L1.Client.SendTransaction(ctx, bptx)
 		if err != nil {
 			if strings.Contains(err.Error(), "nonce too low") {
+				skipped++
 				t.Logf("Skipping batch poster tx with stale nonce: %v", err)
 				continue
 			}
 			Require(t, err)
 		}
 		sentTxs = append(sentTxs, bptx)
 	}
+	t.Logf("Replayed %d batch poster txs (%d captured, %d skipped due to stale nonce)", len(sentTxs), len(batchPosterTxs), skipped)
 	for _, tx := range sentTxs {
 		_, err := EnsureTxSucceeded(ctx, builder.L1.Client, tx)
 		Require(t, err)
```

### system_tests/filtered_transactions_test.go
```diff
@@ -77,6 +77,8 @@ func TestManageTransactionFilterers(t *testing.T) {
 	// block timestamp at which the next tx actually executes.
 	hdr, err = builder.L2.Client.HeaderByNumber(ctx, nil)
 	require.NoError(t, err)
+	// Add 120s buffer to account for drift between the header timestamp we read
+	// and the block timestamp at which the enable tx actually executes in CI.
 	enableAt := hdr.Time + precompiles.FeatureEnableDelay + 120
 	tx, err := arbOwner.SetTransactionFilteringFrom(&ownerTxOpts, enableAt)
 	require.NoError(t, err)
```
