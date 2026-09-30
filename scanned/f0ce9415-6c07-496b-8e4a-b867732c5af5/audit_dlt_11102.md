# [?] fix(tx-submitter): prevent panic by returning error (#713)

## Summary
Severity: Unknown
Chain: Morph
Component: morph-l2/morph
Published: 2025-01-20
Source: https://github.com/morph-l2/morph/commit/72ceffc870a33b6d0ceab5f3ed3a83196b84e3c1
Type: security-commit

## Details
fix(tx-submitter): prevent panic by returning error (#713)

## Patch
### tx-submitter/services/rollup.go
```diff
@@ -1192,7 +1192,7 @@ func (r *Rollup) ReSubmitTx(resend bool, tx *ethtypes.Transaction) (*ethtypes.Tr
 
 	tip, gasFeeCap, blobFeeCap, err := r.GetGasTipAndCap()
 	if err != nil {
-		log.Error("get tip and cap", "err", err)
+		return nil, fmt.Errorf("get gas tip and cap error:%w", err)
 	}
 	if !resend {
 		// bump tip & feeCap
```
