# [?] fix incorrect panic message

## Summary
Severity: Unknown
Chain: Neutron
Component: neutron-org/neutron
Published: 2025-07-28
Source: https://github.com/neutron-org/neutron/commit/bf994848eac60c37870392ba3494e2ec4d14f108
Type: security-commit

## Details
fix incorrect panic message

## Patch
### x/dex/types/price.go
```diff
@@ -69,7 +69,7 @@ func CalcPrice(relativeTickIndex int64) (math_utils.PrecDec, error) {
 
 func BinarySearchPriceToTick(price math_utils.PrecDec) uint64 {
 	if price.LT(math_utils.OnePrecDec()) {
-		panic("Can only lookup prices <= 1")
+		panic("Can only lookup prices >= 1")
 	}
 	var left uint64 // = 0
 	right := MaxTickExp
```
