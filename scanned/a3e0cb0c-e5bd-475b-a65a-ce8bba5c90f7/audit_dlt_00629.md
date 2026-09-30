# [?] fix: excess overflow in `gastime.Time.Tick()` (#297)

## Summary
Severity: Unknown
Chain: Avalanche
Component: ava-labs/avalanchego
Published: 2026-03-25
Source: https://github.com/ava-labs/avalanchego/commit/bdcda4ab0f25242ef63f326e9bf19c599b5dc258
Type: security-commit

## Details
fix: excess overflow in `gastime.Time.Tick()` (#297)

Although this could only occur under extreme circumstances (e.g. scaling
due to min-price change) it still requires handling. The fuzzer could
only find 3 interesting cases for the new `intmath.BoundedAdd()` (more
included via `f.Add()` though) so I had to reduce the minimum required
corpus size.

## Patch
### .github/workflows/go.yml
```diff
@@ -105,14 +105,13 @@ jobs:
       FUNCTION: ${{ matrix.function }}
       CORPUS_DIR: ./${{ matrix.package }}/testdata/fuzz/${{ matrix.function }}
       # The actual corpus size is dependent on the test in question and how many
-      # "interesting" cases can be found. This is an arbitrary lower bound,
-      # chosen as approximately half the size of the very basic
-      # `FuzzEffectiveGasTip`.
-      MIN_CORPUS_SIZE: 20
+      # "interesting" cases can be found. This only ensures that the corpus
+      # extension has actually been performed.
+      MIN_CORPUS_SIZE: 1
     steps:
       - uses: actions/checkout@v4
       - name: Require existing corpus of at least ${MIN_CORPUS_SIZE}
-        run: | # Raw `go test` will be meaningful, and `-fuzz` won't start from nowhere
+        run: |
           [ -d "${CORPUS_DIR}" ] && [ $(ls "${CORPUS_DIR}" | wc -l) -gt ${MIN_CORPUS_SIZE} ]
       - name: Set up Go
         uses: actions/setup-go@v5
```

### gastime/gastime.go
```diff
@@ -192,7 +192,7 @@ func (tm *Time) Tick(g gas.Gas) {
 
 	R, T := tm.Rate(), tm.Target()
 	quo, _, _ := intmath.MulDiv(g, R-T, R) // overflow is impossible as (R-T)/R < 1
-	tm.excess += quo
+	tm.excess = intmath.BoundedAdd(tm.excess, quo, math.MaxUint64)
 }
 
 // FastForwardTo is equivalent to [proxytime.Time.FastForwardTo] except that it
```

### gastime/gastime_test.go
```diff
@@ -421,3 +421,14 @@ func TestNoExcessOverflow(t *testing.T) {
 	tm.FastForwardTo(1, 0)
 	require.Less(t, tm.Excess(), gas.Gas(math.MaxUint64), "Excess() after capped and then fast-forwarding")
 }
+
+func TestTickExcessOverflow(t *testing.T) {
+	const (
+		shortFall   = 2
+		startExcess = math.MaxUint64 - shortFall
+		tick        = TargetToRate * (1 + shortFall) // increases excess by 1+shortFall -> overflow risk
+	)
+	tm := mustNew(t, time.Unix(0, 0), 1, startExcess, DefaultGasPriceConfig())
+	tm.Tick(tick)
+	require.Greater(t, tm.Excess(), gas.Gas(startExcess), "Excess() must increase after Tick(>1)")
+}
```

### intmath/intmath.go
```diff
@@ -22,6 +22,14 @@ func BoundedSubtract[T constraints.Unsigned](a, b, floor T) T {
 	return a - b
 }
 
+// BoundedAdd returns `min(a+b,ceil)` without overflow.
+func BoundedAdd[T constraints.Unsigned](a, b, ceil T) T {
+	if b >= ceil || a >= ceil-b {
+		return ceil
+	}
+	return a + b
+}
+
 // BoundedMultiply returns `min(a*b,ceil)` without overflow.
 func BoundedMultiply[T constraints.Unsigned](a, b, ceil T) T {
 	if b != 0 && a > ceil/b {
```

### intmath/intmath_test.go
```diff
@@ -6,6 +6,7 @@ package intmath
 import (
 	"errors"
 	"math"
+	"math/bits"
 	"math/rand/v2"
 	"testing"
 )
@@ -32,6 +33,48 @@ func TestBoundedSubtract(t *testing.T) {
 	}
 }
 
+func FuzzBoundedAdd(f *testing.F) {
+	test := func(tb testing.TB, a, b, ceil, want uint64) {
+		tb.Helper()
+		if got := BoundedAdd(a, b, ceil); got != want {
+			f.Errorf("BoundedAdd[%T](%[1]d, %d, %d) got %d; want %d", a, b, ceil, got, want)
+		}
+	}
+
+	tests := []struct {
+		a, b, ceil, want uint64
+	}{
+		{a: 0, b: 10, ceil: 0, want: 0},
+		{a: 0, b: 10, ceil: 9, want: 9},
+		{a: 1, b: 10, ceil: 9, want: 9},
+		{a: 1, b: 10, ceil: 10, want: 10},
+		{a: 1, b: 10, ceil: 11, want: 11},
+		{a: 1, b: 10, ceil: 12, want: 11},
+		{a: max, b: 0, ceil: 100, want: 100},
+		{a: max, b: 1, ceil: 100, want: 100},
+		{a: max, b: max, ceil: 0, want: 0},
+	}
+
+	for _, tt := range tests {
+		test(f, tt.a, tt.b, tt.ceil, tt.want)
+		test(f, tt.b, tt.a, tt.ceil, tt.want)
+
+		f.Add(tt.a, tt.b, tt.ceil)
+		f.Add(tt.b, tt.a, tt.ceil)
+	}
+
+	f.Fuzz(func(t *testing.T, a, b, ceil uint64) {
+		// Although similar (there are only so many ways to skin this cat), this
+		// is not an identical inlining of the implementation, especially near
+		// [math.MaxUint64].
+		if _, carry := bits.Add64(a, b, 0); carry == 0 {
+			test(t, a, b, ceil, min(a+b, ceil))
+		} else {
+			test(t, a, b, ceil, min(math.MaxUint64, ceil))
+		}
+	})
+}
+
 func TestBoundedMultiply(t *testing.T) {
 	tests := []struct {
 		a, b, ceil, want uint64
```

### intmath/testdata/fuzz/FuzzBoundedAdd/739185b17eae30dc
```diff
@@ -0,0 +1,4 @@
+go test fuzz v1
+uint64(96)
+uint64(0)
+uint64(55)
```

### intmath/testdata/fuzz/FuzzBoundedAdd/87b290e4d54dc979
```diff
@@ -0,0 +1,4 @@
+go test fuzz v1
+uint64(0)
+uint64(6)
+uint64(0)
```

### intmath/testdata/fuzz/FuzzBoundedAdd/effcaecb9ffe1233
```diff
@@ -0,0 +1,4 @@
+go test fuzz v1
+uint64(0)
+uint64(0)
+uint64(55)
```
