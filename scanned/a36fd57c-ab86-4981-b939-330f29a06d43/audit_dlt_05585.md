# [?] fix: use platform independent method for counting new multiplication overflow from result limb count (#916)

## Summary
Severity: Unknown
Chain: ZK
Component: Consensys/gnark
Published: 2023-11-15
Source: https://github.com/Consensys/gnark/commit/5c18f4540c0735a71db71cceee77c6c8f714c2a8
Type: security-commit

## Details
fix: use platform independent method for counting new multiplication overflow from result limb count (#916)

* fix: use bits.Len for universal computation of multiplication overflow

* fix: handle edge case in multiplication limb count

* fix: define default number of limbs in div and inv precond

## Patch
### std/math/emulated/field_ops.go
```diff
@@ -3,8 +3,8 @@ package emulated
 import (
 	"errors"
 	"fmt"
-	"math"
 	"math/big"
+	"math/bits"
 
 	"github.com/consensys/gnark/frontend"
 )
@@ -15,7 +15,7 @@ func (f *Field[T]) Div(a, b *Element[T]) *Element[T] {
 }
 
 func (f *Field[T]) divPreCond(a, b *Element[T]) (nextOverflow uint, err error) {
-	mulOf, err := f.mulPreCond(&Element[T]{overflow: 0}, b)
+	mulOf, err := f.mulPreCond(&Element[T]{Limbs: make([]frontend.Variable, f.fParams.NbLimbs()), overflow: 0}, b)
 	if err != nil {
 		return mulOf, err
 	}
@@ -45,7 +45,7 @@ func (f *Field[T]) Inverse(a *Element[T]) *Element[T] {
 }
 
 func (f *Field[T]) inversePreCond(a, _ *Element[T]) (nextOverflow uint, err error) {
-	mulOf, err := f.mulPreCond(a, &Element[T]{overflow: 0}) // order is important, we want that reduce left side
+	mulOf, err := f.mulPreCond(a, &Element[T]{Limbs: make([]frontend.Variable, f.fParams.NbLimbs()), overflow: 0}) // order is important, we want that reduce left side
 	if err != nil {
 		return mulOf, err
 	}
@@ -199,7 +199,11 @@ func (f *Field[T]) MulConst(a *Element[T], c *big.Int) *Element[T] {
 func (f *Field[T]) mulPreCond(a, b *Element[T]) (nextOverflow uint, err error) {
 	reduceRight := a.overflow < b.overflow
 	nbResLimbs := nbMultiplicationResLimbs(len(a.Limbs), len(b.Limbs))
-	nextOverflow = f.fParams.BitsPerLimb() + uint(math.Log2(float64(2*nbResLimbs-1))) + 1 + a.overflow + b.overflow
+	nbLimbsOverflow := uint(1)
+	if nbResLimbs > 0 {
+		nbLimbsOverflow = uint(bits.Len(uint(2*nbResLimbs - 1)))
+	}
+	nextOverflow = f.fParams.BitsPerLimb() + nbLimbsOverflow + a.overflow + b.overflow
 	if nextOverflow > f.maxOverflow() {
 		err = overflowError{op: "mul", nextOverflow: nextOverflow, maxOverflow: f.maxOverflow(), reduceRight: reduceRight}
 	}
```

### std/math/emulated/hints.go
```diff
@@ -43,7 +43,11 @@ func (f *Field[T]) computeMultiplicationHint(leftLimbs, rightLimbs []frontend.Va
 // nbMultiplicationResLimbs returns the number of limbs which fit the
 // multiplication result.
 func nbMultiplicationResLimbs(lenLeft, lenRight int) int {
-	return lenLeft + lenRight - 1
+	res := lenLeft + lenRight - 1
+	if res < 0 {
+		res = 0
+	}
+	return res
 }
 
 // MultiplicationHint unpacks the factors and parameters from inputs, computes
```
