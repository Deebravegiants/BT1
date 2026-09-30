# [?] fix: branch with unchecked cast could panic at compile time (#1234)

## Summary
Severity: Unknown
Chain: ZK
Component: Consensys-Incorporated/gnark
Published: 2024-08-02
Source: https://github.com/Consensys-Incorporated/gnark/commit/ea53f373f45d2f9ad9cc1639c34359a35f771191
Type: security-commit

## Details
fix: branch with unchecked cast could panic at compile time (#1234)

## Patch
### frontend/cs/scs/api_assertions.go
```diff
@@ -87,8 +87,10 @@ func (builder *builder) AssertIsEqual(i1, i2 frontend.Variable) {
 // AssertIsDifferent fails if i1 == i2
 func (builder *builder) AssertIsDifferent(i1, i2 frontend.Variable) {
 	s := builder.Sub(i1, i2)
-	if c, ok := builder.constantValue(s); ok && c.IsZero() {
-		panic("AssertIsDifferent(x,x) will never be satisfied")
+	if c, ok := builder.constantValue(s); ok {
+		if c.IsZero() {
+			panic("AssertIsDifferent(x,x) will never be satisfied")
+		}
 	} else if t := s.(expr.Term); t.Coeff.IsZero() {
 		panic("AssertIsDifferent(x,x) will never be satisfied")
 	}
```
