# [?] fix: plonk.Commit race condition

## Summary
Severity: Unknown
Chain: ZK
Component: Consensys-Incorporated/gnark
Published: 2023-03-24
Source: https://github.com/Consensys-Incorporated/gnark/commit/5209bbf39033033fadb3f4bf098ea3e47fa1e9b8
Type: security-commit

## Details
fix: plonk.Commit race condition

## Patch
### constraint/bls12-377/r1cs_sparse.go
```diff
@@ -358,7 +358,7 @@ func (cs *SparseR1CS) computeHints(c constraint.SparseR1C, solution *solution) (
 // if it doesn't, then this function returns and does nothing
 func (cs *SparseR1CS) solveConstraint(c constraint.SparseR1C, solution *solution, coefficientsNegInv fr.Vector) error {
 
-	if c.Commitment != constraint.NOT { // a constraint of the form f_L - PI_2 = 0 or f_L = Comm.
+	if c.Commitment == constraint.COMMITTED { // a constraint of the form f_L - PI_2 = 0 or f_L = Comm.
 		return nil // these are there for enforcing the correctness of the commitment and can be skipped in solving time
 	}
 
```

### constraint/bls12-381/r1cs_sparse.go
```diff
@@ -358,7 +358,7 @@ func (cs *SparseR1CS) computeHints(c constraint.SparseR1C, solution *solution) (
 // if it doesn't, then this function returns and does nothing
 func (cs *SparseR1CS) solveConstraint(c constraint.SparseR1C, solution *solution, coefficientsNegInv fr.Vector) error {
 
-	if c.Commitment != constraint.NOT { // a constraint of the form f_L - PI_2 = 0 or f_L = Comm.
+	if c.Commitment == constraint.COMMITTED { // a constraint of the form f_L - PI_2 = 0 or f_L = Comm.
 		return nil // these are there for enforcing the correctness of the commitment and can be skipped in solving time
 	}
 
```

### constraint/bls24-315/r1cs_sparse.go
```diff
@@ -358,7 +358,7 @@ func (cs *SparseR1CS) computeHints(c constraint.SparseR1C, solution *solution) (
 // if it doesn't, then this function returns and does nothing
 func (cs *SparseR1CS) solveConstraint(c constraint.SparseR1C, solution *solution, coefficientsNegInv fr.Vector) error {
 
-	if c.Commitment != constraint.NOT { // a constraint of the form f_L - PI_2 = 0 or f_L = Comm.
+	if c.Commitment == constraint.COMMITTED { // a constraint of the form f_L - PI_2 = 0 or f_L = Comm.
 		return nil // these are there for enforcing the correctness of the commitment and can be skipped in solving time
 	}
 
```

### constraint/bls24-317/r1cs_sparse.go
```diff
@@ -358,7 +358,7 @@ func (cs *SparseR1CS) computeHints(c constraint.SparseR1C, solution *solution) (
 // if it doesn't, then this function returns and does nothing
 func (cs *SparseR1CS) solveConstraint(c constraint.SparseR1C, solution *solution, coefficientsNegInv fr.Vector) error {
 
-	if c.Commitment != constraint.NOT { // a constraint of the form f_L - PI_2 = 0 or f_L = Comm.
+	if c.Commitment == constraint.COMMITTED { // a constraint of the form f_L - PI_2 = 0 or f_L = Comm.
 		return nil // these are there for enforcing the correctness of the commitment and can be skipped in solving time
 	}
 
```

### constraint/bn254/r1cs_sparse.go
```diff
@@ -195,8 +195,6 @@ func (cs *SparseR1CS) solve(witness fr.Vector, opt solver.Config) (fr.Vector, er
 
 }
 
-var SolveSequentially = false
-
 func (cs *SparseR1CS) parallelSolve(solution *solution, coefficientsNegInv fr.Vector) error {
 	// minWorkPerCPU is the minimum target number of constraint a task should hold
 	// in other words, if a level has less than minWorkPerCPU, it will not be parallelized and executed
@@ -210,19 +208,13 @@ func (cs *SparseR1CS) parallelSolve(solution *solution, coefficientsNegInv fr.Ve
 	chTasks := make(chan []int, runtime.NumCPU())
 	chError := make(chan *UnsatisfiedConstraintError, runtime.NumCPU())
 
-	var m sync.Mutex
-
 	// start a worker pool
 	// each worker wait on chTasks
 	// a task is a slice of constraint indexes to be solved
 	for i := 0; i < runtime.NumCPU(); i++ {
 		go func() {
 			for t := range chTasks {
 				for _, i := range t {
-					if SolveSequentially {
-						m.Lock()
-					}
-					//fmt.Println("solving constraint", i)
 					// for each constraint in the task, solve it.
 					if err := cs.solveConstraint(cs.Constraints[i], solution, coefficientsNegInv); err != nil {
 						chError <- &UnsatisfiedConstraintError{CID: i, Err: err}
@@ -239,9 +231,6 @@ func (cs *SparseR1CS) parallelSolve(solution *solution, coefficientsNegInv fr.Ve
 						wg.Done()
 						return
 					}
-					if SolveSequentially {
-						m.Unlock()
-					}
 				}
 				wg.Done()
 			}
@@ -369,7 +358,7 @@ func (cs *SparseR1CS) computeHints(c constraint.SparseR1C, solution *solution) (
 // if it doesn't, then this function returns and does nothing
 func (cs *SparseR1CS) solveConstraint(c constraint.SparseR1C, solution *solution, coefficientsNegInv fr.Vector) error {
 
-	if c.Commitment != constraint.NOT { // a constraint of the form f_L - PI_2 = 0 or f_L = Comm.
+	if c.Commitment == constraint.COMMITTED { // a constraint of the form f_L - PI_2 = 0 or f_L = Comm.
 		return nil // these are there for enforcing the correctness of the commitment and can be skipped in solving time
 	}
 
```

### constraint/bw6-633/r1cs_sparse.go
```diff
@@ -358,7 +358,7 @@ func (cs *SparseR1CS) computeHints(c constraint.SparseR1C, solution *solution) (
 // if it doesn't, then this function returns and does nothing
 func (cs *SparseR1CS) solveConstraint(c constraint.SparseR1C, solution *solution, coefficientsNegInv fr.Vector) error {
 
-	if c.Commitment != constraint.NOT { // a constraint of the form f_L - PI_2 = 0 or f_L = Comm.
+	if c.Commitment == constraint.COMMITTED { // a constraint of the form f_L - PI_2 = 0 or f_L = Comm.
 		return nil // these are there for enforcing the correctness of the commitment and can be skipped in solving time
 	}
 
```

### constraint/bw6-761/r1cs_sparse.go
```diff
@@ -358,7 +358,7 @@ func (cs *SparseR1CS) computeHints(c constraint.SparseR1C, solution *solution) (
 // if it doesn't, then this function returns and does nothing
 func (cs *SparseR1CS) solveConstraint(c constraint.SparseR1C, solution *solution, coefficientsNegInv fr.Vector) error {
 
-	if c.Commitment != constraint.NOT { // a constraint of the form f_L - PI_2 = 0 or f_L = Comm.
+	if c.Commitment == constraint.COMMITTED { // a constraint of the form f_L - PI_2 = 0 or f_L = Comm.
 		return nil // these are there for enforcing the correctness of the commitment and can be skipped in solving time
 	}
 
```

### constraint/tinyfield/r1cs_sparse.go
```diff
@@ -358,7 +358,7 @@ func (cs *SparseR1CS) computeHints(c constraint.SparseR1C, solution *solution) (
 // if it doesn't, then this function returns and does nothing
 func (cs *SparseR1CS) solveConstraint(c constraint.SparseR1C, solution *solution, coefficientsNegInv fr.Vector) error {
 
-	if c.Commitment != constraint.NOT { // a constraint of the form f_L - PI_2 = 0 or f_L = Comm.
+	if c.Commitment == constraint.COMMITTED { // a constraint of the form f_L - PI_2 = 0 or f_L = Comm.
 		return nil // these are there for enforcing the correctness of the commitment and can be skipped in solving time
 	}
 
```

### internal/generator/backend/template/representations/r1cs.sparse.go.tmpl
```diff
@@ -348,7 +348,7 @@ func (cs *SparseR1CS) computeHints(c constraint.SparseR1C, solution *solution) (
 // if it doesn't, then this function returns and does nothing
 func (cs *SparseR1CS) solveConstraint(c constraint.SparseR1C, solution *solution, coefficientsNegInv fr.Vector) error {
 
-	if c.Commitment != constraint.NOT { // a constraint of the form f_L - PI_2 = 0 or f_L = Comm.
+	if c.Commitment == constraint.COMMITTED { // a constraint of the form f_L - PI_2 = 0 or f_L = Comm.
 		return nil // these are there for enforcing the correctness of the commitment and can be skipped in solving time
 	}
 
```

### std/math/emulated/element_test.go
```diff
@@ -3,7 +3,6 @@ package emulated
 import (
 	"crypto/rand"
 	"fmt"
-	cs "github.com/consensys/gnark/constraint/bn254"
 	"math/big"
 	"reflect"
 	"testing"
@@ -38,14 +37,8 @@ func testName[T FieldParams]() string {
 
 func TestAssertLimbEqualityNoOverflow(t *testing.T) {
 	testAssertLimbEqualityNoOverflow[Goldilocks](t)
-	//testAssertLimbEqualityNoOverflow[Secp256k1Fp](t)
-	//testAssertLimbEqualityNoOverflow[BN254Fp](t)
-}
-
-func TestAssertLimbEqualityNoOverflowSequential(t *testing.T) {
-	cs.SolveSequentially = true
-	testAssertLimbEqualityNoOverflow[Goldilocks](t)
-	cs.SolveSequentially = false
+	testAssertLimbEqualityNoOverflow[Secp256k1Fp](t)
+	testAssertLimbEqualityNoOverflow[BN254Fp](t)
 }
 
 func testAssertLimbEqualityNoOverflow[T FieldParams](t *testing.T) {
```
