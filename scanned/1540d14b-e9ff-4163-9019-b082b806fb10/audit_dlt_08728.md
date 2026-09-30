# [?] op-e2e/actions: unskip TestCrossLayerUser_Default, add txpool.Sync calls to prevent race condition in CI lag (#16881)

## Summary
Severity: Unknown
Chain: Optimism
Component: ethereum-optimism/optimism
Published: 2025-07-29
Source: https://github.com/ethereum-optimism/optimism/commit/9545936bdf621160da8396c8ee18ab05665811e1
Type: security-commit

## Details
op-e2e/actions: unskip TestCrossLayerUser_Default, add txpool.Sync calls to prevent race condition in CI lag (#16881)

## Patch
### op-e2e/actions/helpers/l1_miner.go
```diff
@@ -145,6 +145,7 @@ func (s *L1Miner) ActL1IncludeTx(from common.Address) Action {
 			t.InvalidAction("no tx inclusion when not building l1 block")
 			return
 		}
+		require.NoError(t, s.Eth.TxPool().Sync(), "must sync tx-pool to get accurate pending txs")
 		getPendingIndex := func(from common.Address) uint64 {
 			return s.pendingIndices[from]
 		}
```

### op-e2e/actions/helpers/l2_engine.go
```diff
@@ -205,6 +205,7 @@ func (e *L2Engine) ActL2IncludeTxIgnoreForcedEmpty(from common.Address) Action {
 			e.log.Info("Ignoring e.L2ForceEmpty=true")
 		}
 
+		require.NoError(t, e.Eth.TxPool().Sync(), "must sync tx-pool to get accurate pending txs")
 		tx := firstValidTx(t, from, e.EngineApi.PendingIndices, e.Eth.TxPool().ContentFrom, e.EthClient().NonceAt)
 		prevState := e.EngineApi.ForcedEmpty()
 		e.EngineApi.SetForceEmpty(false) // ensure the engine API can include it
@@ -229,6 +230,7 @@ func (e *L2Engine) ActL2IncludeTx(from common.Address) Action {
 			return
 		}
 
+		require.NoError(t, e.Eth.TxPool().Sync(), "must sync tx-pool to get accurate pending txs")
 		tx := firstValidTx(t, from, e.EngineApi.PendingIndices, e.Eth.TxPool().ContentFrom, e.EthClient().NonceAt)
 		_, err := e.EngineApi.IncludeTx(tx, from)
 		if errors.Is(err, engineapi.ErrNotBuildingBlock) {
```

### op-e2e/actions/helpers/user_test.go
```diff
@@ -71,7 +71,6 @@ func (tc *hardforkScheduledTest) fork(fork string) **hexutil.Uint64 {
 }
 
 func TestCrossLayerUser_Default(t *testing.T) {
-	t.Skipf("skipping due to high flakiness")
 	testCrossLayerUser(t, config.DefaultAllocType)
 }
 
```
