# [?] Fix: Build on 32-bit arch would raise int overflow https://github.com/Consensys/gnark/issues/1192 (#1195)

## Summary
Severity: Unknown
Chain: ZK
Component: Consensys-Incorporated/gnark
Published: 2024-07-11
Source: https://github.com/Consensys-Incorporated/gnark/commit/1da452b71d9259685d93ed121fc0c0e45ab636b9
Type: security-commit

## Details
Fix: Build on 32-bit arch would raise int overflow https://github.com/Consensys/gnark/issues/1192 (#1195)

## Patch
### std/rangecheck/rangecheck_commit.go
```diff
@@ -154,10 +154,10 @@ func (c *commitChecker) getOptimalBasewidth(api frontend.API) int {
 }
 
 func optimalWidth(countFn func(baseLength int, collected []checkedVariable) int, collected []checkedVariable) int {
-	min := math.MaxInt64
+	min := int64(math.MaxInt64)
 	minVal := 0
 	for j := 2; j < 18; j++ {
-		current := countFn(j, collected)
+		current := int64(countFn(j, collected))
 		if current < min {
 			min = current
 			minVal = j
```
