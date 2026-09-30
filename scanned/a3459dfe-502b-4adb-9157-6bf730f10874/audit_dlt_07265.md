# [?] Fix flaky TestRateLimitErrorFormat and mock block encode data race (#4130)

## Summary
Severity: Unknown
Chain: Sei
Component: sei-protocol/sei-chain
Published: 2026-09-10
Source: https://github.com/sei-protocol/sei-chain/commit/09504a19da7e7d6c74ce018f62a7a33ea613fd2e
Type: security-commit

## Details
Fix flaky TestRateLimitErrorFormat and mock block encode data race (#4130)

`TestSimulationAPIRequestLimiter/TestRateLimitErrorFormat` fires 20
concurrent calls and asserts that at least one is rejected by the rate
limiter with the expected error text. On an overloaded runner a single
burst can be serialized enough by the scheduler that the limiter never
trips, so zero errors are observed and the assertion fails. Separately,
running the test under `-race` reports a data race on main:
`MockClient.mockBlock` calls `Encoder(Tx1)` on every block fetch, and
the auth tx wrapper memoizes encoded bytes on first use, so concurrent
simulate calls write to the shared `Tx1` concurrently.

The fix retries a synchronized burst against a fresh `testEnv` up to 5
times until a rejection is observed (the pattern
`TestDifferentMethodsShareSameLimiter` already uses), and encodes the
mock block txs once in fixture setup (`Tx1Bz`,
`TxNonEvmWithSyntheticLogBz`) so the mock block only reads immutable
byte slices.

Flaked in:
https://github.com/sei-protocol/sei-chain/actions/runs/34329926916/job/102395953394

## Patch
### evmrpc/setup_test.go
```diff
@@ -127,6 +127,12 @@ var DebugTraceNonPanicTx sdk.Tx
 var DebugTraceSyntheticTx sdk.Tx
 var TxNonEvm sdk.Tx
 var TxNonEvmWithSyntheticLog sdk.Tx
+
+// Tx1Bz and TxNonEvmWithSyntheticLogBz are encoded once in init: the tx
+// encoder memoizes into the tx wrapper, which is unsafe under the concurrent
+// mockBlock calls made by rate-limiter tests.
+var Tx1Bz []byte
+var TxNonEvmWithSyntheticLogBz []byte
 var UnconfirmedTx sdk.Tx
 
 var SConfig = evmrpc.SimulateConfig{GasCap: 10000000, MaxStateOverrideAccounts: 100, MaxStateOverrideSlots: 1000}
@@ -304,16 +310,7 @@ func (c *MockClient) mockBlock(height int64) *coretypes.ResultBlock {
 		Block: &tmtypes.Block{
 			Header: mockBlockHeader(height),
 			Data: tmtypes.Data{
-				Txs: []tmtypes.Tx{
-					func() []byte {
-						bz, _ := Encoder(Tx1)
-						return bz
-					}(),
-					func() []byte {
-						bz, _ := Encoder(TxNonEvmWithSyntheticLog)
-						return bz
-					}(),
-				},
+				Txs: []tmtypes.Tx{Tx1Bz, TxNonEvmWithSyntheticLogBz},
 			},
 			LastCommit: &tmtypes.Commit{
 				Height: MockHeight8 - 1,
@@ -937,6 +934,9 @@ func generateTxData() {
 	TestSyntheticTxHash = syntheticEthTx.Hash().Hex()
 	TxNonEvm = app.TestTx{}
 	TxNonEvmWithSyntheticLog = app.TestTx{}
+	Tx1Bz = mustEncode(Tx1)
+	// app.TestTx is rejected by the encoder and appears in blocks as empty bytes.
+	TxNonEvmWithSyntheticLogBz = nil
 	bloomTx1 := ethtypes.CreateBloom(&ethtypes.Receipt{Logs: []*ethtypes.Log{{
 		Address: common.HexToAddress("0x1111111111111111111111111111111111111111"),
 		Topics: []common.Hash{common.HexToHash("0x1111111111111111111111111111111111111111111111111111111111111111"),
@@ -1009,6 +1009,14 @@ func generateTxData() {
 	EVMKeeper.SetAddressMapping(Ctx, sdk.AccAddress(tracerTestTxFrom[:]), tracerTestTxFrom)
 }
 
+func mustEncode(tx sdk.Tx) []byte {
+	bz, err := Encoder(tx)
+	if err != nil {
+		panic(err)
+	}
+	return bz
+}
+
 func buildTx(txData ethtypes.DynamicFeeTx) (client.TxBuilder, *ethtypes.Transaction) {
 	chainId := big.NewInt(config.DefaultChainID)
 	mnemonic := "fish mention unlock february marble dove vintage sand hub ordinary fade found inject room embark supply fabric improve spike stem give current similar glimpse"
```

### evmrpc/simulate_test.go
```diff
@@ -971,29 +971,44 @@ func TestSimulationAPIRequestLimiter(t *testing.T) {
 	})
 
 	t.Run("TestRateLimitErrorFormat", func(t *testing.T) {
-		tEnv := newTestEnv(t)
-		// Test the error message format by overwhelming the rate limiter
-		const numRequests = 20
-		results := make(chan error, numRequests)
-		start := make(chan struct{})
-		var wg sync.WaitGroup
-
-		// Release all requests at once to reliably saturate the limiter.
-		for range numRequests {
-			wg.Go(func() {
-				<-start
-				_, err := tEnv.simAPI.Call(t.Context(), tEnv.args, nil, nil, nil)
-				results <- err
-			})
+		// Test the error message format by overwhelming the rate limiter.
+		// A single burst can occasionally avoid contention on overloaded CI workers,
+		// so retry a synchronized burst a few times.
+		const (
+			numRequests = 20
+			maxAttempts = 5
+		)
+		runBurst := func(tEnv *testEnv) []error {
+			results := make(chan error, numRequests)
+			start := make(chan struct{})
+			var wg sync.WaitGroup
+
+			// Release all requests at once to saturate the limiter.
+			for range numRequests {
+				wg.Go(func() {
+					<-start
+					_, err := tEnv.simAPI.Call(t.Context(), tEnv.args, nil, nil, nil)
+					results <- err
+				})
+			}
+			close(start)
+			wg.Wait()
+			close(results)
+
+			var rateLimitErrors []error
+			for err := range results {
+				if err != nil && strings.Contains(err.Error(), "rejected due to rate limit") {
+					rateLimitErrors = append(rateLimitErrors, err)
+				}
+			}
+			return rateLimitErrors
 		}
-		close(start)
-		wg.Wait()
-		close(results)
 
 		var rateLimitErrors []error
-		for err := range results {
-			if err != nil && strings.Contains(err.Error(), "rejected due to rate limit") {
-				rateLimitErrors = append(rateLimitErrors, err)
+		for range maxAttempts {
+			rateLimitErrors = runBurst(newTestEnv(t))
+			if len(rateLimitErrors) > 0 {
+				break
 			}
 		}
 
```
