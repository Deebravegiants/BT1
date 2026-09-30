# [?] execution: fix deadlock in block building when run in envs with 1 erigon block builder (#17213)

## Summary
Severity: Unknown
Chain: Ethereum
Component: erigontech/erigon
Published: 2025-09-23
Source: https://github.com/erigontech/erigon/commit/29bc2cd3556fc401ba446cd825e7d56cb78f8cff
Type: security-commit

## Details
execution: fix deadlock in block building when run in envs with 1 erigon block builder (#17213)

closes https://github.com/erigontech/erigon/issues/17041

## Patch
### .github/workflows/test-hive.yml
```diff
@@ -93,7 +93,7 @@ jobs:
             fi
           }
           run_suite engine exchange-capabilities 0
-          run_suite engine withdrawals 2
+          run_suite engine withdrawals 0
           run_suite engine cancun 0
           run_suite engine api 0
           # run_suite engine auth 0
```

### execution/stagedsync/exec3.go
```diff
@@ -829,6 +829,14 @@ Loop:
 		return errExhausted
 	}
 
+	if !shouldReportToTxPool && cfg.notifications != nil && cfg.notifications.Accumulator != nil && !isMining && b != nil {
+		// No reporting to the txn pool has been done since we are not within the "state-stream" window.
+		// However, we should still at the very least report the last block number to it, so it can update its block progress.
+		// Otherwise, we can get in a deadlock situation when there is a block building request in environments where
+		// the Erigon process is the only block builder (e.g. some Hive tests, kurtosis testnets with one erigon block builder, etc.)
+		cfg.notifications.Accumulator.StartChange(b.HeaderNoCopy(), nil, false /* unwind */)
+	}
+
 	return nil
 }
 
```
