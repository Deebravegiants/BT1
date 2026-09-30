# [?] Merge pull request #970 from 2dvorak/fix/gasless-queue-nolimit-overflow

## Summary
Severity: Unknown
Chain: Kaia
Component: kaiachain/kaia
Published: 2026-06-29
Source: https://github.com/kaiachain/kaia/commit/05bc77b469def13cb61d1120ea98ce53c60bd1b7
Type: security-commit

## Details
Merge pull request #970 from 2dvorak/fix/gasless-queue-nolimit-overflow

gasless: fix no-limit queue check rejecting all bundle txs

## Patch
### kaiax/gasless/impl/tx_pool.go
```diff
@@ -44,7 +44,7 @@ func (g *GaslessModule) PreAddTx(tx *types.Transaction, local bool) error {
 	}
 
 	if g.IsBundleTx(tx) {
-		if g.knownTxs.numQueue() >= int(g.GetMaxBundleTxsInQueue()) {
+		if uint(g.knownTxs.numQueue()) >= g.GetMaxBundleTxsInQueue() {
 			return ErrBundleTxQueueFull
 		}
 		g.knownTxs.add(tx, TxStatusQueue)
```

### kaiax/gasless/impl/tx_pool_test.go
```diff
@@ -17,6 +17,7 @@
 package impl
 
 import (
+	"math"
 	"math/big"
 	"math/rand/v2"
 	"testing"
@@ -82,6 +83,48 @@ func TestIsModuleTx(t *testing.T) {
 	}
 }
 
+func TestPreAddTxQueueLimit(t *testing.T) {
+	log.EnableLogForTest(log.LvlError, log.LvlTrace)
+
+	newModule := func(maxQueue uint) *GaslessModule {
+		cfg := *gasless.DefaultGaslessConfig()
+		cfg.MaxBundleTxsInQueue = maxQueue
+		g := NewGaslessModule()
+		dbm := database.NewMemoryDBManager()
+		backend := backends.NewSimulatedBackendWithDatabase(dbm, testAllocStorage(), testChainConfig)
+		nodekey, _ := crypto.GenerateKey()
+		require.NoError(t, g.Init(&InitOpts{
+			ChainConfig:   testChainConfig,
+			GaslessConfig: &cfg,
+			NodeKey:       nodekey,
+			Chain:         backend.BlockChain(),
+			NodeType:      common.ENDPOINTNODE,
+		}))
+		return g
+	}
+
+	bundleTx := func() *types.Transaction {
+		privkey, _ := crypto.GenerateKey()
+		return makeApproveTx(t, privkey, 0, ApproveArgs{Spender: common.HexToAddress("0x1234"), Amount: abi.MaxUint256})
+	}
+
+	// --gasless.max-bundle-txs-in-queue <= 0 maps to the math.MaxUint64 "no limit"
+	// sentinel (config.go).
+	t.Run("no limit sentinel accepts on empty queue", func(t *testing.T) {
+		g := newModule(math.MaxUint64)
+		tx := bundleTx()
+		require.True(t, g.IsBundleTx(tx))
+		require.NoError(t, g.PreAddTx(tx, false))
+		require.Equal(t, 1, g.knownTxs.numQueue())
+	})
+
+	t.Run("finite limit still enforced", func(t *testing.T) {
+		g := newModule(1)
+		require.NoError(t, g.PreAddTx(bundleTx(), false))
+		require.ErrorIs(t, g.PreAddTx(bundleTx(), false), ErrBundleTxQueueFull)
+	})
+}
+
 func TestIsReady(t *testing.T) {
 	log.EnableLogForTest(log.LvlError, log.LvlTrace)
 
```
