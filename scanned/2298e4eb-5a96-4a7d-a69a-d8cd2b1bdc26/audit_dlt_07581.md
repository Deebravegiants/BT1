# [?] tests: fix test panic (#30741)

## Summary
Severity: Unknown
Chain: Ethereum
Component: ethereum/go-ethereum
Published: 2024-11-10
Source: https://github.com/ethereum/go-ethereum/commit/77f3ef3714afa280add3654ebceda2dd1856d65f
Type: security-commit

## Details
tests: fix test panic (#30741)

Fix panic in tests

## Patch
### tests/state_test_util.go
```diff
@@ -308,6 +308,7 @@ func (t *StateTest) RunNoVerify(subtest StateSubtest, vmconfig vm.Config, snapsh
 		if tracer := evm.Config.Tracer; tracer != nil && tracer.OnTxEnd != nil {
 			evm.Config.Tracer.OnTxEnd(nil, err)
 		}
+		return st, common.Hash{}, 0, err
 	}
 	// Add 0-value mining reward. This only makes a difference in the cases
 	// where
@@ -322,7 +323,7 @@ func (t *StateTest) RunNoVerify(subtest StateSubtest, vmconfig vm.Config, snapsh
 		receipt := &types.Receipt{GasUsed: vmRet.UsedGas}
 		tracer.OnTxEnd(receipt, nil)
 	}
-	return st, root, vmRet.UsedGas, err
+	return st, root, vmRet.UsedGas, nil
 }
 
 func (t *StateTest) gasLimit(subtest StateSubtest) uint64 {
```
