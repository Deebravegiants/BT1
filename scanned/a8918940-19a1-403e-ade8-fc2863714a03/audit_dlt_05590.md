# [?] fix: subtraction overflow computation bug (#579)

## Summary
Severity: Unknown
Chain: ZK
Component: Consensys/gnark
Published: 2023-03-16
Source: https://github.com/Consensys/gnark/commit/0e81df4897a3d1617a559dccca7bfa959a23eb55
Type: security-commit

## Details
fix: subtraction overflow computation bug (#579)

* feat: add subtraction without inline reduction

* fix: count possible overflow due to subtraction padding

Previously when estimating the maximal overflow for subtraction we only
considered the possible overflow caused by the subtraction padding and the
subtrahend. But actually as the padding may overflow the minuend we have to
also consider it.

Due to this, we also had to decrease the maximal possible overflow by one as
modular reduction uses subtraction as a subroutine.

* test: update circuit statistics

* fix: remove empty branch

## Patch
### std/math/emulated/field.go
```diff
@@ -278,7 +278,7 @@ func (f *Field[T]) compactLimbs(e *Element[T], groupSize, bitsPerLimb uint) []fr
 // then the limbs may overflow the native field.
 func (f *Field[T]) maxOverflow() uint {
 	f.maxOfOnce.Do(func() {
-		f.maxOf = uint(f.api.Compiler().FieldBitLen()-1) - f.fParams.BitsPerLimb()
+		f.maxOf = uint(f.api.Compiler().FieldBitLen()-2) - f.fParams.BitsPerLimb()
 	})
 	return f.maxOf
 }
```

### std/math/emulated/field_assert.go
```diff
@@ -128,7 +128,7 @@ func (f *Field[T]) AssertIsEqual(a, b *Element[T]) {
 		return
 	}
 
-	diff := f.Sub(b, a)
+	diff := f.subNoReduce(b, a)
 
 	// we compute k such that diff / p == k
 	// so essentially, we say "I know an element k such that k*p == diff"
```

### std/math/emulated/field_ops.go
```diff
@@ -225,9 +225,20 @@ func (f *Field[T]) Sub(a, b *Element[T]) *Element[T] {
 	return f.reduceAndOp(f.sub, f.subPreCond, a, b)
 }
 
+// subReduce returns a-b and returns it. Contrary to [Field[T].Sub] method this
+// method does not reduce the inputs if the result would overflow. This method
+// is currently only used as a subroutine in [Field[T].Reduce] method to avoid
+// infinite recursion when we are working exactly on the overflow limits.
+func (f *Field[T]) subNoReduce(a, b *Element[T]) *Element[T] {
+	nextOverflow, _ := f.subPreCond(a, b)
+	// we ignore error as it only indicates if we should reduce or not. But we
+	// are in non-reducing version of sub.
+	return f.sub(a, b, nextOverflow)
+}
+
 func (f *Field[T]) subPreCond(a, b *Element[T]) (nextOverflow uint, err error) {
-	reduceRight := a.overflow < b.overflow+2
-	nextOverflow = max(b.overflow+2, a.overflow)
+	reduceRight := (a.overflow + 1) < (b.overflow + 1)
+	nextOverflow = max(b.overflow+1, a.overflow+1)
 	if nextOverflow > f.maxOverflow() {
 		err = overflowError{op: "sub", nextOverflow: nextOverflow, maxOverflow: f.maxOverflow(), reduceRight: reduceRight}
 	}
```
