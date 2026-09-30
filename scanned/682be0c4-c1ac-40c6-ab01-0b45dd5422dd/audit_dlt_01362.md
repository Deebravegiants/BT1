# [?] miner: fix race condition in tests (#1651)

## Summary
Severity: Unknown
Chain: Polygon
Component: maticnetwork/bor
Published: 2025-07-22
Source: https://github.com/0xPolygon/bor/commit/c302516193cdfa3f0d3b6434ea1aa7e47513169d
Type: security-commit

## Details
miner: fix race condition in tests (#1651)

Use a new config for all tests (some of which run in parallel) instead of using a global test config which can cause race conditions if some fields (like commit interrupt) are modified for some tests.

## Patch
### miner/worker_test.go
```diff
@@ -89,7 +89,7 @@ func testGenerateBlockAndImport(t *testing.T, isClique bool, isBor bool) {
 
 	defer engine.Close()
 
-	w, b, _ := newTestWorker(t, &chainConfig, engine, db, false, 0)
+	w, b, _ := newTestWorker(t, DefaultTestConfig(), &chainConfig, engine, db, false, 0)
 	defer w.close()
 
 	// This test chain imports the mined blocks.
@@ -173,12 +173,6 @@ var (
 	// Test transactions
 	pendingTxs []*types.Transaction
 	newTxs     []*types.Transaction
-
-	testConfig = &Config{
-		Recommit:            time.Second,
-		GasCeil:             params.GenesisGasLimit,
-		CommitInterruptFlag: true,
-	}
 )
 
 func init() {
@@ -214,6 +208,14 @@ func init() {
 	newTxs = append(newTxs, tx2)
 }
 
+func DefaultTestConfig() *Config {
+	return &Config{
+		Recommit:            time.Second,
+		GasCeil:             params.GenesisGasLimit,
+		CommitInterruptFlag: true,
+	}
+}
+
 // testWorkerBackend implements worker.Backend interfaces and wraps all information needed during the testing.
 type testWorkerBackend struct {
 	db      ethdb.Database
@@ -315,10 +317,10 @@ func (b *testWorkerBackend) newStorageContractCallTx(to common.Address, nonce ui
 	return tx
 }
 
-func newTestWorker(t TensingObject, chainConfig *params.ChainConfig, engine consensus.Engine, db ethdb.Database, noempty bool, delay uint) (*worker, *testWorkerBackend, func()) {
+func newTestWorker(t TensingObject, config *Config, chainConfig *params.ChainConfig, engine consensus.Engine, db ethdb.Database, noempty bool, delay uint) (*worker, *testWorkerBackend, func()) {
 	backend := newTestWorkerBackend(t, chainConfig, engine, db)
 	backend.txPool.Add(pendingTxs, false)
-	w := newWorker(testConfig, chainConfig, engine, backend, new(event.TypeMux), nil, false)
+	w := newWorker(config, chainConfig, engine, backend, new(event.TypeMux), nil, false)
 	w.setMockTxDelay(delay)
 	w.setEtherbase(testBankAddress)
 	// enable empty blocks
@@ -335,7 +337,7 @@ func TestGenerateAndImportBlock(t *testing.T) {
 	config.Clique = &params.CliqueConfig{Period: 1, Epoch: 30000}
 	engine := clique.New(config.Clique, db)
 
-	w, b, _ := newTestWorker(t, &config, engine, db, false, 0)
+	w, b, _ := newTestWorker(t, DefaultTestConfig(), &config, engine, db, false, 0)
 	defer w.close()
 
 	// This test chain imports the mined blocks.
@@ -407,7 +409,7 @@ func testEmptyWork(t *testing.T, chainConfig *params.ChainConfig, engine consens
 	t.Helper()
 	defer engine.Close()
 
-	w, _, _ := newTestWorker(t, chainConfig, engine, rawdb.NewMemoryDatabase(), false, 0)
+	w, _, _ := newTestWorker(t, DefaultTestConfig(), chainConfig, engine, rawdb.NewMemoryDatabase(), false, 0)
 	defer w.close()
 
 	taskCh := make(chan struct{}, 2)
@@ -454,7 +456,7 @@ func TestAdjustIntervalClique(t *testing.T) {
 func testAdjustInterval(t *testing.T, chainConfig *params.ChainConfig, engine consensus.Engine) {
 	defer engine.Close()
 
-	w, _, _ := newTestWorker(t, chainConfig, engine, rawdb.NewMemoryDatabase(), false, 0)
+	w, _, _ := newTestWorker(t, DefaultTestConfig(), chainConfig, engine, rawdb.NewMemoryDatabase(), false, 0)
 	defer w.close()
 
 	w.skipSealHook = func(task *task) bool {
@@ -559,7 +561,7 @@ func TestGetSealingWorkPostMerge(t *testing.T) {
 func testGetSealingWork(t *testing.T, chainConfig *params.ChainConfig, engine consensus.Engine) {
 	defer engine.Close()
 
-	w, b, _ := newTestWorker(t, chainConfig, engine, rawdb.NewMemoryDatabase(), false, 0)
+	w, b, _ := newTestWorker(t, DefaultTestConfig(), chainConfig, engine, rawdb.NewMemoryDatabase(), false, 0)
 	defer w.close()
 
 	w.setExtra([]byte{0x01, 0x02})
@@ -721,14 +723,13 @@ func testCommitInterruptExperimentBor(t *testing.T, delay uint, txCount int) {
 		txs         = make([]*types.Transaction, 0, txInTxpool)
 	)
 
-	testConfig.CommitInterruptFlag = true
 	chainConfig = params.BorUnittestChainConfig
 
 	log.SetDefault(log.NewLogger(log.NewTerminalHandlerWithLevel(os.Stderr, log.LevelInfo, true)))
 
 	engine, ctrl = getFakeBorFromConfig(t, chainConfig)
 
-	w, b, _ := newTestWorker(t, chainConfig, engine, rawdb.NewMemoryDatabase(), true, delay)
+	w, b, _ := newTestWorker(t, DefaultTestConfig(), chainConfig, engine, rawdb.NewMemoryDatabase(), true, delay)
 	defer func() {
 		w.close()
 		engine.Close()
@@ -770,15 +771,14 @@ func TestCommitInterruptExperimentBor_NewTxFlow(t *testing.T) {
 		ctrl        *gomock.Controller
 	)
 
-	testConfig.CommitInterruptFlag = true
 	chainConfig = params.BorUnittestChainConfig
 
 	log.SetDefault(log.NewLogger(log.NewTerminalHandlerWithLevel(os.Stderr, log.LevelInfo, true)))
 
 	engine, ctrl = getFakeBorFromConfig(t, chainConfig)
 
 	// Set the mock tx delay to 500ms
-	w, b, _ := newTestWorker(t, chainConfig, engine, rawdb.NewMemoryDatabase(), true, 500)
+	w, b, _ := newTestWorker(t, DefaultTestConfig(), chainConfig, engine, rawdb.NewMemoryDatabase(), true, 500)
 	defer func() {
 		w.close()
 		engine.Close()
@@ -855,8 +855,9 @@ func TestCommitInterruptPending(t *testing.T) {
 
 	// Disable the commit interrupt as this will cause a reset on every block which we don't want
 	// for this test.
+	testConfig := DefaultTestConfig()
 	testConfig.CommitInterruptFlag = false
-	w, b, _ := newTestWorker(t, chainConfig, engine, rawdb.NewMemoryDatabase(), true, 0)
+	w, b, _ := newTestWorker(t, testConfig, chainConfig, engine, rawdb.NewMemoryDatabase(), true, 0)
 	defer func() {
 		w.close()
 		engine.Close()
@@ -931,7 +932,7 @@ func BenchmarkBorMining(b *testing.B) {
 
 	chainConfig.LondonBlock = big.NewInt(0)
 
-	w, back, _ := newTestWorker(b, chainConfig, engine, rawdb.NewMemoryDatabase(), false, 0)
+	w, back, _ := newTestWorker(b, DefaultTestConfig(), chainConfig, engine, rawdb.NewMemoryDatabase(), false, 0)
 	defer w.close()
 
 	chain, _ := core.NewBlockChain(rawdb.NewMemoryDatabase(), nil, back.genesis, nil, engine, vm.Config{}, nil, nil, nil)
@@ -1030,7 +1031,7 @@ func BenchmarkBorMiningBlockSTMMetadata(b *testing.B) {
 
 	chainConfig.LondonBlock = big.NewInt(0)
 
-	w, back, _ := newTestWorker(b, chainConfig, engine, rawdb.NewMemoryDatabase(), false, 0)
+	w, back, _ := newTestWorker(b, DefaultTestConfig(), chainConfig, engine, rawdb.NewMemoryDatabase(), false, 0)
 	defer w.close()
 
 	// This test chain imports the mined blocks.
```
