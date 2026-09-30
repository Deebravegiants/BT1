# [?] piecefunc: prevent overflow

## Summary
Severity: Unknown
Chain: Sonic
Component: 0xsoniclabs/sonic
Published: 2021-12-15
Source: https://github.com/0xsoniclabs/sonic/commit/ce0e398b6e67d08419dba5ff5192743ac97f9da1
Type: security-commit

## Details
piecefunc: prevent overflow

## Patch
### gossip/emitter/piecefuncs.go
```diff
@@ -1,8 +1,6 @@
 package emitter
 
 import (
-	"math"
-
 	"github.com/Fantom-foundation/lachesis-base/emitter/ancestor"
 	"github.com/Fantom-foundation/lachesis-base/inter/idx"
 
@@ -60,7 +58,7 @@ var (
 			Y: 0.999 * piecefunc.DecimalUnit,
 		},
 		{
-			X: math.MaxUint32 * piecefunc.DecimalUnit,
+			X: 10000.0 * piecefunc.DecimalUnit,
 			Y: 0.9999 * piecefunc.DecimalUnit,
 		},
 	})
@@ -90,10 +88,6 @@ var (
 			X: 1.0 * piecefunc.DecimalUnit,
 			Y: 1.0 * piecefunc.DecimalUnit,
 		},
-		{ // event metric is never above 1.0
-			X: math.MaxUint32 * piecefunc.DecimalUnit,
-			Y: 1.0 * piecefunc.DecimalUnit,
-		},
 	})
 	validatorsToOverheadF = piecefunc.NewFunc([]piecefunc.Dot{
 		{
@@ -117,7 +111,7 @@ var (
 			Y: 0.9 * piecefunc.DecimalUnit,
 		},
 		{
-			X: math.MaxUint32,
+			X: 1000,
 			Y: 1.0 * piecefunc.DecimalUnit,
 		},
 	})
```

### utils/piecefunc/piecefunc.go
```diff
@@ -1,8 +1,11 @@
 package piecefunc
 
+import "math"
+
 const (
 	// DecimalUnit is used to define ratios with integers, it's 1.0
 	DecimalUnit = 1e6
+	maxVal      = math.MaxUint64/uint64(DecimalUnit) - 1
 )
 
 // Dot is a pair of numbers
@@ -25,6 +28,12 @@ func NewFunc(dots []Dot) func(x uint64) uint64 {
 		if i >= 1 && dot.X <= prevX {
 			panic("non monotonic X")
 		}
+		if dot.Y > maxVal {
+			panic("too large Y")
+		}
+		if dot.X > maxVal {
+			panic("too large X")
+		}
 		prevX = dot.X
 	}
 
```

### utils/piecefunc/piecefunc_test.go
```diff
@@ -24,12 +24,12 @@ func TestConstFunc(t *testing.T) {
 			Y: 1.0 * DecimalUnit,
 		},
 		{
-			X: math.MaxUint32 * DecimalUnit,
+			X: 0xFFFFFF * DecimalUnit,
 			Y: 1.0 * DecimalUnit,
 		},
 	})
 
-	for i, x := range []uint64{0, 1, 5, 10, 20, 0xFFFF, math.MaxUint32} {
+	for i, x := range []uint64{0, 1, 5, 10, 20, 0xFFFF, 0xFFFFFF} {
 		X := x * DecimalUnit
 		Y := constF(X)
 		require.Equal(uint64(DecimalUnit), Y, i)
@@ -53,7 +53,7 @@ func TestUp45Func(t *testing.T) {
 			Y: 20.0 * DecimalUnit,
 		},
 		{
-			X: math.MaxUint32 * DecimalUnit,
+			X: 0xFFFFFF * DecimalUnit,
 			Y: 21.0 * DecimalUnit,
 		},
 	})
@@ -64,7 +64,7 @@ func TestUp45Func(t *testing.T) {
 		require.Equal(X, Y, i)
 	}
 
-	for i, x := range []uint64{21, 0xFFFF, math.MaxUint32} {
+	for i, x := range []uint64{21, 0xFFFF, 0xFFFFFF} {
 		X := x * DecimalUnit
 		Y := up45F(X)
 		require.True(20.0*DecimalUnit <= Y && Y <= 21.0*DecimalUnit, i)
```
