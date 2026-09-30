# [?] rpcdaemon:  modify Error in case of result = nil to avoid panic (#16766)

## Summary
Severity: Unknown
Chain: Ethereum
Component: erigontech/erigon
Published: 2025-08-22
Source: https://github.com/erigontech/erigon/commit/274c2ab864fc9265e2e8f043323ec55a760b0e19
Type: security-commit

## Details
rpcdaemon:  modify Error in case of result = nil to avoid panic (#16766)

## Patch
### execution/exec3/trace_worker.go
```diff
@@ -139,6 +139,9 @@ func (e *TraceWorker) ExecTxn(txNum uint64, txIndex int, txn types.Transaction,
 	} else {
 		result, err := core.ApplyMessage(e.evm, msg, gp, true /* refunds */, gasBailout /* gasBailout */, e.engine)
 		if err != nil {
+			if result == nil {
+				return fmt.Errorf("%w: blockNum=%d, txNum=%d", err, e.blockNum, txNum)
+			}
 			return fmt.Errorf("%w: blockNum=%d, txNum=%d, %s", err, e.blockNum, txNum, result.Err)
 		}
 	}
```
