# [?] Merge pull request #271 from qianbin/fix-panic-invalid-bloom-k

## Summary
Severity: Unknown
Chain: VeChain
Component: vechain/thor
Published: 2019-06-26
Source: https://github.com/vechain/thor/commit/2b8cb62a37d823d37b5fe6999091da2ac32e7748
Type: security-commit

## Details
Merge pull request #271 from qianbin/fix-panic-invalid-bloom-k

fix(API): panic on invalid bloom K

## Patch
### thor/bloom.go
```diff
@@ -15,7 +15,7 @@ func EstimateBloomK(itemCount int) int {
 	if k > maxK {
 		return maxK
 	}
-	if k < 0 {
+	if k < 1 {
 		return 1
 	}
 	return k
```
