# [?] fix: IsZero throws panic on (#367)

## Summary
Severity: Unknown
Chain: ZK
Component: Consensys/gnark
Published: 2022-09-14
Source: https://github.com/Consensys-Incorporated/gnark/commit/57c06660f6df95f3b096b70633abf22ac3b371ab
Type: security-commit

## Details
fix: IsZero throws panic on (#367)

* fix: IsZero bug causing Cmp throw

A code will trigger the bug:

func isNegative(api frontend.API, x frontend.Variable) frontend.Variable {
	c := frontend.Variable("10944121435919637611123202872628637544274182200208017171849102093287904247808")
	return api.Cmp(x, c)
}

* test: IsZero test for constants

Co-authored-by: Tiancheng Xie <tianc.x@berkeley.edu>

## Patch
### frontend/cs/scs/api.go
```diff
@@ -352,7 +352,7 @@ func (system *scs) Lookup2(b0, b1 frontend.Variable, i0, i1, i2, i3 frontend.Var
 func (system *scs) IsZero(i1 frontend.Variable) frontend.Variable {
 	if a, ok := system.ConstantValue(i1); ok {
 		if !(a.IsUint64() && a.Uint64() == 0) {
-			panic("input should be zero")
+			return 0
 		}
 		return 1
 	}
```

### internal/backend/circuits/iszero.go
```diff
@@ -13,8 +13,12 @@ func (circuit *isZero) Define(api frontend.API) error {
 
 	a := api.IsZero(circuit.X)
 	b := api.IsZero(circuit.Y)
+	c := api.IsZero(1)
+	d := api.IsZero(0)
 	api.AssertIsEqual(a, 1)
 	api.AssertIsEqual(b, 0)
+	api.AssertIsEqual(c, 0)
+	api.AssertIsEqual(d, 1)
 
 	return nil
 }
```
