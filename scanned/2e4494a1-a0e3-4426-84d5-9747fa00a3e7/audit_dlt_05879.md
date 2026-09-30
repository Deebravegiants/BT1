# [?] fix(prover): index-out-of-range panic in merkle proof verification (#3453)

## Summary
Severity: Unknown
Chain: Linea
Component: Consensys/linea-monorepo
Published: 2026-06-26
Source: https://github.com/LFDT-Lineth/lineth-monorepo/commit/ea9dc73d6de8e6da4f5e3a72fc2a0ece97b9b2ea
Type: security-commit

## Details
fix(prover): index-out-of-range panic in merkle proof verification (#3453)

* fix(prover): make CoWindowRange cover all windows, not just the last

CoWindowRange set foundAny only after an early continue, so it stayed
false: each padded window overwrote start/stop instead of being merged,
leaving the min/max union as dead code. Combining two distinct windows
returned only the last window's range.

Set foundAny in the first branch so the range spans every window.

* fix(prover): fix index-out-of-range panic in Merkle proof verification

TernaryCtx.Run iterated i <= stop over the half-open range returned by
CoCompactRange, reading one element past the end when the active range
reached the last row of the column. This panicked with "index out of
range [N] with length N" during Merkle proof verification on near-full
state-manager batches.

## Patch
### prover/maths/common/smartvectors/smartvectors.go
```diff
@@ -639,12 +639,12 @@ func CoWindowRange(sv ...SmartVector) (start, stop int) {
 			if !foundAny {
 				start = s.Offset()
 				stop = s.Offset() + len(s.Window())
+				foundAny = true
 				continue
 			}
 
 			start = min(start, s.Offset())
 			stop = max(stop, s.Offset()+len(s.Window()))
-			foundAny = true
 		}
 	}
 
```

### prover/maths/common/smartvectors/windowed_test.go
```diff
@@ -64,3 +64,28 @@ func TestEdgeCases(t *testing.T) {
 	},
 		"NewConstant.Subvector should panic with 'zero length are not allowed' message")
 }
+
+// TestCoWindowRange checks that the range covers the union of every window,
+// independently of argument order, and that constants are skipped.
+func TestCoWindowRange(t *testing.T) {
+	const size = 16
+	a := NewPaddedCircularWindow(vector.Rand(3), field.Zero(), 2, size) // [2, 5)
+	b := NewPaddedCircularWindow(vector.Rand(4), field.Zero(), 8, size) // [8, 12)
+	c := NewConstant(field.Zero(), size)
+
+	start, stop := CoWindowRange(a, b)
+	require.Equal(t, 2, start)
+	require.Equal(t, 12, stop)
+
+	start, stop = CoWindowRange(b, a)
+	require.Equal(t, 2, start)
+	require.Equal(t, 12, stop)
+
+	start, stop = CoWindowRange(c, a, c)
+	require.Equal(t, 2, start)
+	require.Equal(t, 5, stop)
+
+	start, stop = CoWindowRange(NewRegular(vector.Rand(size)), a)
+	require.Equal(t, 0, start)
+	require.Equal(t, size, stop)
+}
```

### prover/protocol/dedicated/ternary.go
```diff
@@ -77,7 +77,7 @@ func (ctx *TernaryCtx) Run(run *wizard.ProverRuntime) {
 		res         = make([]field.Element, 0, stop-start)
 	)
 
-	for i := start; i <= stop; i++ {
+	for i := start; i < stop; i++ {
 
 		c := condition.Get(i)
 
```

### prover/protocol/dedicated/ternary_test.go
```diff
@@ -0,0 +1,85 @@
+package dedicated
+
+import (
+	"fmt"
+	"testing"
+
+	sv "github.com/consensys/linea-monorepo/prover/maths/common/smartvectors"
+	"github.com/consensys/linea-monorepo/prover/maths/common/vector"
+	"github.com/consensys/linea-monorepo/prover/maths/field"
+	"github.com/consensys/linea-monorepo/prover/protocol/compiler/dummy"
+	"github.com/consensys/linea-monorepo/prover/protocol/wizard"
+	"github.com/stretchr/testify/require"
+)
+
+// TestTernary checks [Ternary] over constant, full and padded-window inputs.
+// Full vectors and end-anchored windows cover the case where the active range
+// reaches the last row, which previously read past the end of the column.
+func TestTernary(t *testing.T) {
+
+	const size = 8
+
+	boolShapes := []sv.SmartVector{
+		sv.NewConstant(field.Zero(), size),
+		sv.NewConstant(field.One(), size),
+		sv.ForTest(0, 1, 0, 1, 0, 1, 0, 1),
+		sv.ForTest(1, 1, 1, 1, 1, 1, 1, 1),
+		sv.NewPaddedCircularWindow(vector.ForTest(1, 0, 1, 0), field.Zero(), 0, size),
+		sv.NewPaddedCircularWindow(vector.ForTest(1, 0, 1, 0), field.Zero(), 2, size),
+		sv.NewPaddedCircularWindow(vector.ForTest(1, 0, 1, 0), field.Zero(), 4, size),
+	}
+
+	valShapes := []sv.SmartVector{
+		sv.NewConstant(field.NewElement(7), size),
+		sv.ForTest(10, 11, 12, 13, 14, 15, 16, 17),
+		sv.NewPaddedCircularWindow(vector.ForTest(1, 2, 3, 4), field.NewElement(42), 0, size),
+		sv.NewPaddedCircularWindow(vector.ForTest(1, 2, 3, 4), field.NewElement(42), 4, size),
+	}
+
+	runCase := func(t *testing.T, cond, ifTrue, ifFalse sv.SmartVector) {
+
+		var ctx *TernaryCtx
+
+		define := func(b *wizard.Builder) {
+			c := b.RegisterCommit("COND", size)
+			tCol := b.RegisterCommit("IF_TRUE", size)
+			fCol := b.RegisterCommit("IF_FALSE", size)
+			ctx = Ternary(b.CompiledIOP, c, tCol, fCol)
+		}
+
+		prover := func(run *wizard.ProverRuntime) {
+			run.AssignColumn("COND", cond)
+			run.AssignColumn("IF_TRUE", ifTrue)
+			run.AssignColumn("IF_FALSE", ifFalse)
+
+			ctx.Run(run)
+
+			res := ctx.Result.GetColAssignment(run)
+			for k := 0; k < size; k++ {
+				want := ifFalse.Get(k)
+				c := cond.Get(k)
+				if !c.IsZero() {
+					want = ifTrue.Get(k)
+				}
+				got := res.Get(k)
+				require.Truef(t, want.Equal(&got), "row #%v: want %v got %v", k, want.String(), got.String())
+			}
+		}
+
+		comp := wizard.Compile(define, dummy.Compile)
+		proof := wizard.Prove(comp, prover)
+		if err := wizard.Verify(comp, proof); err != nil {
+			t.Fatalf("verifier did not accept: %v", err.Error())
+		}
+	}
+
+	for ci, cond := range boolShapes {
+		for ti, ifTrue := range valShapes {
+			for fi, ifFalse := range valShapes {
+				t.Run(fmt.Sprintf("cond-%v-true-%v-false-%v", ci, ti, fi), func(t *testing.T) {
+					runCase(t, cond, ifTrue, ifFalse)
+				})
+			}
+		}
+	}
+}
```
