# [?] Fix `evm` statetest crash (#14449)

## Summary
Severity: Unknown
Chain: Ethereum
Component: erigontech/erigon
Published: 2025-04-04
Source: https://github.com/erigontech/erigon/commit/67fad81d760201d14eb7278bed2ef839f3c189c9
Type: security-commit

## Details
Fix `evm` statetest crash (#14449)

Fixes #14386

## Patch
### tests/state_test_util.go
```diff
@@ -264,14 +264,21 @@ func (t *StateTest) RunNoVerify(tx kv.RwTx, subtest StateSubtest, vmconfig vm.Co
 		}
 	}
 	evm := vm.NewEVM(context, txContext, statedb, config, vmconfig)
+	if vmconfig.Tracer != nil && vmconfig.Tracer.OnTxStart != nil {
+		vmconfig.Tracer.OnTxStart(evm.GetVMContext(), nil, libcommon.Address{})
+	}
 
 	// Execute the message.
 	snapshot := statedb.Snapshot()
 	gaspool := new(core.GasPool)
 	gaspool.AddGas(block.GasLimit()).AddBlobGas(config.GetMaxBlobGasPerBlock(header.Time))
-	if _, err = core.ApplyMessage(evm, msg, gaspool, true /* refunds */, false /* gasBailout */, nil /* engine */); err != nil {
+	res, err := core.ApplyMessage(evm, msg, gaspool, true /* refunds */, false /* gasBailout */, nil /* engine */)
+	if err != nil {
 		statedb.RevertToSnapshot(snapshot)
 	}
+	if vmconfig.Tracer != nil && vmconfig.Tracer.OnTxEnd != nil {
+		vmconfig.Tracer.OnTxEnd(&types.Receipt{GasUsed: res.UsedGas}, nil)
+	}
 
 	if err = statedb.FinalizeTx(evm.ChainRules(), w); err != nil {
 		return nil, libcommon.Hash{}, err
```
