# [?] fix finalize panic (#411)

## Summary
Severity: Unknown
Chain: Morph
Component: morph-l2/morph
Published: 2024-07-11
Source: https://github.com/morph-l2/morph/commit/067ee2686c8727a1034979e8203acc313129bb48
Type: security-commit

## Details
fix finalize panic (#411)

## Patch
### tx-submitter/services/rollup.go
```diff
@@ -392,6 +392,10 @@ func (sr *Rollup) finalize() error {
 		)
 		return fmt.Errorf("get next batch by index err:%v", err)
 	}
+	if batch == nil {
+		log.Info("next batch is nil,wait next batch header to finalize", "next_batch_index", nextBatchIndex)
+		return nil
+	}
 
 	// calldata
 	calldata, err := sr.abi.Pack("finalizeBatch", []byte(batch.ParentBatchHeader))
```
