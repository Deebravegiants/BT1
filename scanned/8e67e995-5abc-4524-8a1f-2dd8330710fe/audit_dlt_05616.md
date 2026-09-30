# [?] rpc: fix eth_feeHistory panics for finalized/safe block markers (#23290)

## Summary
Severity: Unknown
Chain: Ethereum
Component: erigontech/erigon
Published: 2026-08-14
Source: https://github.com/erigontech/erigon/commit/958931e9977de020fb527fafbcc31a2c29b8f1bb
Type: security-commit

## Details
rpc: fix eth_feeHistory panics for finalized/safe block markers (#23290)

surfaced during glamsterdam-devnet-7 testing
we weren't correctly handling the special block markers representing
finalized/safe block markers which resulted in panics

## Patch
### rpc/gasprice/feehistory.go
```diff
@@ -253,7 +253,21 @@ func (oracle *Oracle) resolveBlockRange(ctx context.Context, lastBlock rpc.Block
 	}
 	if lastBlock == rpc.LatestBlockNumber {
 		lastBlock = headBlock
-	} else if pendingBlock == nil && lastBlock > headBlock {
+	} else if lastBlock < 0 {
+		// we have known reserved values for special block markers that can be negative
+		if lastBlock < rpc.LatestExecutedBlockNumber {
+			return nil, nil, 0, 0, fmt.Errorf("invalid block number %d", lastBlock)
+		}
+		lastBlockHeader, err := oracle.backend.HeaderByNumber(ctx, lastBlock)
+		if err != nil {
+			return nil, nil, 0, 0, err
+		}
+		if lastBlockHeader == nil {
+			return nil, nil, 0, 0, nil
+		}
+		lastBlock = rpc.BlockNumber(lastBlockHeader.Number.Uint64())
+	}
+	if pendingBlock == nil && lastBlock > headBlock {
 		return nil, nil, 0, 0, fmt.Errorf("%w: requested %d, head %d", ErrRequestBeyondHead, lastBlock, headBlock)
 	}
 	if maxHistory != 0 {
```

### rpc/gasprice/gasprice_test.go
```diff
@@ -272,11 +272,20 @@ func BenchmarkKthPercentile(b *testing.B) {
 // cancelled, allowing us to verify that cancellation propagates correctly
 // through fetchBlockPricesParallel.
 type mockOracleBackend struct {
-	head *types.Header
+	head           *types.Header
+	safeBlock      uint64
+	finalizedBlock uint64
 }
 
-func (m *mockOracleBackend) HeaderByNumber(_ context.Context, _ rpc.BlockNumber) (*types.Header, error) {
-	return m.head, nil
+func (m *mockOracleBackend) HeaderByNumber(_ context.Context, number rpc.BlockNumber) (*types.Header, error) {
+	header := types.CopyHeader(m.head)
+	switch number {
+	case rpc.SafeBlockNumber:
+		header.Number.SetUint64(m.safeBlock)
+	case rpc.FinalizedBlockNumber:
+		header.Number.SetUint64(m.finalizedBlock)
+	}
+	return header, nil
 }
 
 func (m *mockOracleBackend) BlockByNumber(ctx context.Context, _ rpc.BlockNumber) (*types.Block, error) {
@@ -304,6 +313,63 @@ func (m *mockOracleBackend) Fork(_ context.Context) (gasprice.OracleBackend, fun
 	return nil, nil, nil // sequential mode
 }
 
+func TestFeeHistoryResolvesSafeAndFinalizedBlocks(t *testing.T) {
+	head := types.NewEmptyHeaderForAssembling()
+	head.Number.SetUint64(25)
+	head.BaseFee = uint256.NewInt(1)
+	head.GasLimit = 30_000_000
+	head.GasUsed = 15_000_000
+
+	backend := &mockOracleBackend{
+		head:           head,
+		safeBlock:      20,
+		finalizedBlock: 18,
+	}
+	oracle := gasprice.NewOracle(backend, gaspricecfg.Config{
+		Blocks:      1,
+		MaxPrice:    gaspricecfg.DefaultMaxPrice,
+		IgnorePrice: gaspricecfg.DefaultIgnorePrice,
+	}, jsonrpc.NewGasPriceCache(), gasprice.NewFeeHistoryCache(), log.New())
+
+	for _, tc := range []struct {
+		name        string
+		newestBlock rpc.BlockNumber
+		wantOldest  uint64
+	}{
+		{name: "safe", newestBlock: rpc.SafeBlockNumber, wantOldest: 17},
+		{name: "finalized", newestBlock: rpc.FinalizedBlockNumber, wantOldest: 15},
+	} {
+		t.Run(tc.name, func(t *testing.T) {
+			require.NotPanics(t, func() {
+				oldest, reward, baseFee, gasUsedRatio, _, _, err := oracle.FeeHistory(t.Context(), 4, tc.newestBlock, []float64{25})
+				require.NoError(t, err)
+				require.Equal(t, tc.wantOldest, oldest.Uint64())
+				require.Len(t, reward, 4)
+				require.Len(t, baseFee, 5)
+				require.Len(t, gasUsedRatio, 4)
+			})
+		})
+	}
+}
+
+func TestFeeHistoryRejectsUnknownNegativeBlockNumber(t *testing.T) {
+	head := types.NewEmptyHeaderForAssembling()
+	head.Number.SetUint64(25)
+	head.BaseFee = uint256.NewInt(1)
+	head.GasLimit = 30_000_000
+	head.GasUsed = 15_000_000
+
+	backend := &mockOracleBackend{head: head}
+	oracle := gasprice.NewOracle(backend, gaspricecfg.Config{
+		Blocks:      1,
+		MaxPrice:    gaspricecfg.DefaultMaxPrice,
+		IgnorePrice: gaspricecfg.DefaultIgnorePrice,
+	}, jsonrpc.NewGasPriceCache(), gasprice.NewFeeHistoryCache(), log.New())
+
+	_, _, _, _, _, _, err := oracle.FeeHistory(t.Context(), 4, rpc.BlockNumber(-6), nil)
+	require.EqualError(t, err, "invalid block number -6")
+}
+
 // TestSuggestTipCap_EmptyBlocksFallbackMatchesGeth verifies that on a chain
 // where all sampled blocks are empty, the oracle uses GWei/1000 as the
 // fallback price (matching Geth's miner.DefaultConfig.GasPrice) rather than
```
