# [?] fix staking msg conversion crash

## Summary
Severity: Unknown
Chain: Harmony
Component: harmony-one/harmony
Published: 2019-11-27
Source: https://github.com/harmony-one/harmony/commit/a5ad4d89197d4a7fe002601ae135aac82506e730
Type: security-commit

## Details
fix staking msg conversion crash

## Patch
### staking/types/transaction.go
```diff
@@ -39,7 +39,11 @@ func (d *txdata) CopyFrom(d2 *txdata) {
 	restored, _ := RLPDecodeStakeMsg(
 		payload, d2.Directive,
 	)
-	d.StakeMsg = restored.(StakeMsg).Copy()
+	if restored == nil {
+		d.StakeMsg = d2.StakeMsg
+	} else {
+		d.StakeMsg = restored.(StakeMsg).Copy()
+	}
 	d.V = new(big.Int).Set(d2.V)
 	d.R = new(big.Int).Set(d2.R)
 	d.S = new(big.Int).Set(d2.S)
```
