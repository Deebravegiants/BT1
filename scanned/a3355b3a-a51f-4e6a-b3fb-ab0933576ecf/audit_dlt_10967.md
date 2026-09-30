# [?] fix: set overflow after reduce

## Summary
Severity: Unknown
Chain: ZK
Component: Consensys-Incorporated/gnark
Published: 2022-05-19
Source: https://github.com/Consensys-Incorporated/gnark/commit/82ce4d59d2b64bf771528ec326d9b7db282773dd
Type: security-commit

## Details
fix: set overflow after reduce

## Patch
### std/math/nonnative/variable.go
```diff
@@ -383,6 +383,7 @@ func (e *Element) Reduce(a Element) *Element {
 		panic(fmt.Sprintf("reduction hint: %v", err))
 	}
 	e.Limbs = r
+	e.overflow = 0
 	e.EnforceWidth()
 	e.AssertIsEqual(a)
 	return e
```
