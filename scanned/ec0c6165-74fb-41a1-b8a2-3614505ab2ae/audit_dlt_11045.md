# [?] Fix panics in debug_TraceTransaction (#27)

## Summary
Severity: Unknown
Chain: Optimism
Component: ethereum-optimism/op-geth
Published: 2022-11-22
Source: https://github.com/ethereum-optimism/op-geth/commit/28c13bd98d2283f39084b9ecf3619c8b2af41387
Type: security-commit

## Details
Fix panics in debug_TraceTransaction (#27)

* Make sure L1CostFunc is set on returned context

* Fix panic if HistoricalRPCService is not set

* Can we just return nil?

* Simplify

## Patch
### eth/state_accessor.go
```diff
@@ -215,10 +215,10 @@ func (eth *Ethereum) stateAtTransaction(ctx context.Context, block *types.Block,
 		msg, _ := tx.AsMessage(signer, block.BaseFee())
 		txContext := core.NewEVMTxContext(msg)
 		context := core.NewEVMBlockContext(block.Header(), eth.blockchain, nil)
+		context.L1CostFunc = types.NewL1CostFunc(eth.blockchain.Config(), statedb)
 		if idx == txIndex {
 			return msg, context, statedb, release, nil
 		}
-		context.L1CostFunc = types.NewL1CostFunc(eth.blockchain.Config(), statedb)
 		// Not yet the searched for transaction, execute on top of the current state
 		vmenv := vm.NewEVM(context, txContext, statedb, eth.blockchain.Config(), vm.Config{})
 		statedb.SetTxContext(tx.Hash(), idx)
```

### eth/tracers/api.go
```diff
@@ -873,7 +873,7 @@ func (api *API) TraceTransaction(ctx context.Context, hash common.Hash, config *
 	if err != nil {
 		return nil, err
 	}
-	if tx == nil {
+	if tx == nil && api.backend.HistoricalRPCService() != nil {
 		var histResult []*txTraceResult
 		err = api.backend.HistoricalRPCService().CallContext(ctx, &histResult, "debug_traceTransaction", hash, config)
 		if err != nil && err.Error() == "not found" {
```
