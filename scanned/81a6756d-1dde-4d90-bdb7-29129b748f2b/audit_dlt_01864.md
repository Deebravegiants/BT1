# [?] fix(op-interop-filter): prevent uint64 underflow in calculateStartingBlock (#19720)

## Summary
Severity: Unknown
Chain: Optimism
Component: ethereum-optimism/optimism
Published: 2026-03-23
Source: https://github.com/ethereum-optimism/optimism/commit/e7b34fe3fb664cc4b1bbdbfa4602b99fb1fa843e
Type: security-commit

## Details
fix(op-interop-filter): prevent uint64 underflow in calculateStartingBlock (#19720)

When startTimestamp < backfillDuration.Seconds(), the subtraction wraps
around to a large uint64 value. Guard against this by checking before
subtracting and falling back to genesis block.

Fixes runtimeverification/_audits_Ethereum-optimism_optimism_interopv2#37

Co-authored-by: Claude Opus 4.6 (1M context) <noreply@anthropic.com>

## Patch
### op-interop-filter/filter/logsdb_chain_ingester.go
```diff
@@ -340,7 +340,12 @@ func (c *LogsDBChainIngester) findAndSetEarliestBlock(latestBlock uint64) {
 // calculateStartingBlock returns the block number where ingestion should start,
 // calculated from startTimestamp and backfillDuration.
 func (c *LogsDBChainIngester) calculateStartingBlock() uint64 {
-	backfillTimestamp := c.startTimestamp - uint64(c.backfillDuration.Seconds())
+	backfillSeconds := uint64(c.backfillDuration.Seconds())
+	if c.startTimestamp < backfillSeconds {
+		// Backfill reaches before epoch 0; start from genesis
+		return c.rollupCfg.Genesis.L2.Number
+	}
+	backfillTimestamp := c.startTimestamp - backfillSeconds
 
 	startingBlock, err := c.rollupCfg.TargetBlockNumber(backfillTimestamp)
 	if err != nil {
```

### op-interop-filter/filter/logsdb_chain_ingester_test.go
```diff
@@ -633,6 +633,34 @@ func TestLogsDBChainIngester_InitIngestion_FreshStart(t *testing.T) {
 	require.Equal(t, startingBlock, nextBlock)
 }
 
+func TestLogsDBChainIngester_CalculateStartingBlock_BackfillUnderflow(t *testing.T) {
+	chainID := eth.ChainIDFromUInt64(901)
+	tempDir := t.TempDir()
+
+	mockClient := NewMockEthClient()
+
+	l2StartBlock := uint64(100)
+	l2StartTimestamp := uint64(1000)
+
+	headBlock := createTestBlock(200, 1200, common.Hash{0x99})
+	mockClient.AddBlock(headBlock, nil)
+	mockClient.SetHeadBlock(headBlock)
+
+	ingester := newTestLogsDBChainIngester(t, testIngesterConfig{
+		chainID:   chainID,
+		dataDir:   tempDir,
+		ethClient: mockClient,
+		rollupCfg: testRollupConfig(901, l2StartBlock, l2StartTimestamp),
+	})
+
+	// startTimestamp=50, backfillDuration=200s would underflow without the guard
+	ingester.startTimestamp = 50
+	ingester.backfillDuration = 200 * time.Second
+
+	startingBlock := ingester.calculateStartingBlock()
+	require.Equal(t, l2StartBlock, startingBlock)
+}
+
 func TestLogsDBChainIngester_InitIngestion_ResumeFromExistingDB(t *testing.T) {
 	chainID := eth.ChainIDFromUInt64(901)
 	tempDir := t.TempDir()
```
