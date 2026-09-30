# [?] Merge pull request from GHSA-rjjm-x32p-m3f7

## Summary
Severity: Unknown
Chain: ZK
Component: Consensys/gnark
Published: 2023-11-10
Source: https://github.com/Consensys/gnark/commit/f528807119e9443df94b8c01fe8ee65abe3c75d8
Type: security-commit

## Details
Merge pull request from GHSA-rjjm-x32p-m3f7

* test: add failing test case

* refactor: use lsh instead of exp for partition combination

* fix: correct constraining of high limb

* feat: count conditional check during optimisation

* chore: update statistics

## Patch
### internal/regression_tests/issue_897_test.go
```diff
@@ -0,0 +1,32 @@
+package regressiontests
+
+import (
+	"testing"
+
+	"github.com/consensys/gnark/frontend"
+	"github.com/consensys/gnark/std/rangecheck"
+	"github.com/consensys/gnark/test"
+)
+
+type TestRangeCheckCircuit struct {
+	I1 frontend.Variable
+	N  int
+}
+
+func (circuit *TestRangeCheckCircuit) Define(api frontend.API) error {
+	rangeChecker := rangecheck.New(api)
+	rangeChecker.Check(circuit.I1, circuit.N)
+	return nil
+}
+
+func TestIssue897(t *testing.T) {
+	assert := test.NewAssert(t)
+	circuit := TestRangeCheckCircuit{
+		N: 7,
+	}
+	witness := TestRangeCheckCircuit{
+		I1: 1 << 7,
+		N:  7,
+	}
+	assert.CheckCircuit(&circuit, test.WithInvalidAssignment(&witness))
+}
```

### std/rangecheck/rangecheck_commit.go
```diff
@@ -74,7 +74,8 @@ func (c *commitChecker) commit(api frontend.API) error {
 	// decompose into smaller limbs
 	decomposed := make([]frontend.Variable, 0, len(c.collected))
 	collected := make([]frontend.Variable, len(c.collected))
-	base := new(big.Int).Lsh(big.NewInt(1), uint(baseLength))
+	coef := new(big.Int)
+	one := big.NewInt(1)
 	for i := range c.collected {
 		// collect all vars for commitment input
 		collected[i] = c.collected[i].v
@@ -89,9 +90,22 @@ func (c *commitChecker) commit(api frontend.API) error {
 		// check that limbs are correct. We check the sizes of the limbs later
 		var composed frontend.Variable = 0
 		for j := range limbs {
-			composed = api.Add(composed, api.Mul(limbs[j], new(big.Int).Exp(base, big.NewInt(int64(j)), nil)))
+			composed = api.Add(composed, api.Mul(limbs[j], coef.Lsh(one, uint(baseLength*j))))
 		}
 		api.AssertIsEqual(composed, c.collected[i].v)
+		// we have split the input into nbLimbs partitions of length baseLength.
+		// This ensures that the checked variable is not more than
+		// nbLimbs*baseLength bits, but was requested to be c.collected[i].bits,
+		// which may be less. Conditionally add one more check to the most
+		// significant partition. If shift is the difference between
+		// nbLimbs*baseLength and c.collected[i].bits, then check that MS*2^diff
+		// is also baseLength. Because of both checks for MS and MS*2^diff give
+		// ensure that the value are small we cannot have overflow.
+		shift := nbLimbs*baseLength - c.collected[i].bits
+		if shift > 0 {
+			msLimbShifted := api.Mul(limbs[nbLimbs-1], coef.Lsh(one, uint(shift)))
+			decomposed = append(decomposed, msLimbShifted)
+		}
 	}
 	nbTable := 1 << baseLength
 	return logderivarg.Build(api, logderivarg.AsTable(c.buildTable(nbTable)), logderivarg.AsTable(decomposed))
@@ -155,7 +169,11 @@ func optimalWidth(countFn func(baseLength int, collected []checkedVariable) int,
 func nbR1CSConstraints(baseLength int, collected []checkedVariable) int {
 	nbDecomposed := 0
 	for i := range collected {
-		nbDecomposed += int(decompSize(collected[i].bits, baseLength))
+		nbVarLimbs := int(decompSize(collected[i].bits, baseLength))
+		if nbVarLimbs*baseLength > collected[i].bits {
+			nbVarLimbs += 1
+		}
+		nbDecomposed += int(nbVarLimbs)
 	}
 	eqs := len(collected)       // correctness of decomposition
 	nbRight := nbDecomposed     // inverse per decomposed
@@ -166,7 +184,11 @@ func nbR1CSConstraints(baseLength int, collected []checkedVariable) int {
 func nbPLONKConstraints(baseLength int, collected []checkedVariable) int {
 	nbDecomposed := 0
 	for i := range collected {
-		nbDecomposed += int(decompSize(collected[i].bits, baseLength))
+		nbVarLimbs := int(decompSize(collected[i].bits, baseLength))
+		if nbVarLimbs*baseLength > collected[i].bits {
+			nbVarLimbs += 1
+		}
+		nbDecomposed += int(nbVarLimbs)
 	}
 	eqs := nbDecomposed               // check correctness of every decomposition. this is nbDecomp adds + eq cost per collected
 	nbRight := 3 * nbDecomposed       // denominator sub, inv and large sum per table entry
```
