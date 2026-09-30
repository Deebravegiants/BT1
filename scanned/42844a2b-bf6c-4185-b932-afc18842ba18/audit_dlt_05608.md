# [?] eth/tracers: avoid panic in state test runner (#30332)

## Summary
Severity: Unknown
Chain: Ethereum
Component: ethereum/go-ethereum
Published: 2024-08-21
Source: https://github.com/ethereum/go-ethereum/commit/30824faf90bf5d1f5e4a1cf0b50de80f10d16490
Type: security-commit

## Details
eth/tracers: avoid panic in state test runner (#30332)

Make tracers more robust by handling `nil` receipt as input. 
Also pass in a receipt with gas used in the state test runner.
Closes https://github.com/ethereum/go-ethereum/issues/30117.

---------

Co-authored-by: Sina Mahmoodi <itz.s1na@gmail.com>

## Patch
### eth/tracers/js/goja.go
```diff
@@ -275,7 +275,9 @@ func (t *jsTracer) OnTxEnd(receipt *types.Receipt, err error) {
 		}
 		return
 	}
-	t.ctx["gasUsed"] = t.vm.ToValue(receipt.GasUsed)
+	if receipt != nil {
+		t.ctx["gasUsed"] = t.vm.ToValue(receipt.GasUsed)
+	}
 }
 
 // onStart implements the Tracer interface to initialize the tracing operation.
```

### eth/tracers/logger/logger.go
```diff
@@ -268,7 +268,9 @@ func (l *StructLogger) OnTxEnd(receipt *types.Receipt, err error) {
 		}
 		return
 	}
-	l.usedGas = receipt.GasUsed
+	if receipt != nil {
+		l.usedGas = receipt.GasUsed
+	}
 }
 
 // StructLogs returns the captured log entries.
```

### eth/tracers/native/call.go
```diff
@@ -225,7 +225,9 @@ func (t *callTracer) OnTxEnd(receipt *types.Receipt, err error) {
 	if err != nil {
 		return
 	}
-	t.callstack[0].GasUsed = receipt.GasUsed
+	if receipt != nil {
+		t.callstack[0].GasUsed = receipt.GasUsed
+	}
 	if t.config.WithLog {
 		// Logs are not emitted when the call fails
 		clearFailedLogs(&t.callstack[0], false)
```

### tests/state_test_util.go
```diff
@@ -297,19 +297,17 @@ func (t *StateTest) RunNoVerify(subtest StateSubtest, vmconfig vm.Config, snapsh
 
 	if tracer := vmconfig.Tracer; tracer != nil && tracer.OnTxStart != nil {
 		tracer.OnTxStart(evm.GetVMContext(), nil, msg.From)
-		if evm.Config.Tracer.OnTxEnd != nil {
-			defer func() {
-				evm.Config.Tracer.OnTxEnd(nil, err)
-			}()
-		}
 	}
 	// Execute the message.
 	snapshot := st.StateDB.Snapshot()
 	gaspool := new(core.GasPool)
 	gaspool.AddGas(block.GasLimit())
-	_, err = core.ApplyMessage(evm, msg, gaspool)
+	vmRet, err := core.ApplyMessage(evm, msg, gaspool)
 	if err != nil {
 		st.StateDB.RevertToSnapshot(snapshot)
+		if tracer := evm.Config.Tracer; tracer != nil && tracer.OnTxEnd != nil {
+			evm.Config.Tracer.OnTxEnd(nil, err)
+		}
 	}
 	// Add 0-value mining reward. This only makes a difference in the cases
 	// where
@@ -320,6 +318,10 @@ func (t *StateTest) RunNoVerify(subtest StateSubtest, vmconfig vm.Config, snapsh
 
 	// Commit state mutations into database.
 	root, _ = st.StateDB.Commit(block.NumberU64(), config.IsEIP158(block.Number()))
+	if tracer := evm.Config.Tracer; tracer != nil && tracer.OnTxEnd != nil {
+		receipt := &types.Receipt{GasUsed: vmRet.UsedGas}
+		tracer.OnTxEnd(receipt, nil)
+	}
 	return st, root, err
 }
 
```
