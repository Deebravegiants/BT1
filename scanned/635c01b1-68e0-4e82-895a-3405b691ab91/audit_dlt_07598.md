# [?] tests: fix panic via state test runner using json logger (#29349)

## Summary
Severity: Unknown
Chain: Ethereum
Component: ethereum/go-ethereum
Published: 2024-03-26
Source: https://github.com/ethereum/go-ethereum/commit/1dd898c24e85980a3ba9fcc203f00a3ea2f060d6
Type: security-commit

## Details
tests: fix panic via state test runner using json logger (#29349)

* tests: fix panic via state test runner using json logger

* tests: also invoke OnTxEnd

## Patch
### tests/state_test_util.go
```diff
@@ -295,6 +295,14 @@ func (t *StateTest) RunNoVerify(subtest StateSubtest, vmconfig vm.Config, snapsh
 	}
 	evm := vm.NewEVM(context, txContext, st.StateDB, config, vmconfig)
 
+	if tracer := vmconfig.Tracer; tracer != nil && tracer.OnTxStart != nil {
+		tracer.OnTxStart(evm.GetVMContext(), nil, msg.From)
+		if evm.Config.Tracer.OnTxEnd != nil {
+			defer func() {
+				evm.Config.Tracer.OnTxEnd(nil, err)
+			}()
+		}
+	}
 	// Execute the message.
 	snapshot := st.StateDB.Snapshot()
 	gaspool := new(core.GasPool)
```
