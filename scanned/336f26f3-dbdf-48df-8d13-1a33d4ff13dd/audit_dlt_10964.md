# [?] fix: race condition

## Summary
Severity: Unknown
Chain: ZK
Component: Consensys-Incorporated/gnark
Published: 2023-01-19
Source: https://github.com/Consensys-Incorporated/gnark/commit/97a200135cfcaecfa2d5306c02ad0281e12cd117
Type: security-commit

## Details
fix: race condition

## Patch
### constraint/bn254/gkr.go
```diff
@@ -13,7 +13,6 @@ import (
 	"github.com/consensys/gnark/std/utils/algo_utils"
 	"hash"
 	"math/big"
-	"sync"
 )
 
 type gkrSolvingData struct {
@@ -153,7 +152,7 @@ func gkrSetOutputValues(circuit []constraint.GkrWire, assignments gkrAssignment,
 	// Check if outsI == len(outs)?
 }
 
-func gkrSolveHint(data constraint.GkrInfo, res *gkrSolvingData, solvingDone *sync.Mutex) hint.Function {
+func gkrSolveHint(data constraint.GkrInfo, res *gkrSolvingData) hint.Function {
 	return func(_ *big.Int, ins, outs []*big.Int) error {
 
 		res.circuit = convertCircuit(data.Circuit)      // TODO: Take this out of here into the proving module
@@ -166,8 +165,6 @@ func gkrSolveHint(data constraint.GkrInfo, res *gkrSolvingData, solvingDone *syn
 		fmt.Println("assignment ", sliceSliceToString(assignments))
 		fmt.Println("returning ", bigIntPtrSliceToString(outs))
 
-		solvingDone.Unlock()
-
 		return nil
 	}
 }
@@ -199,17 +196,16 @@ func frToBigInts(dst []*big.Int, src []fr.Element) {
 	}
 }
 
-func gkrProveHint(hashName string, data *gkrSolvingData, solvingDone *sync.Mutex) hint.Function {
+func gkrProveHint(hashName string, data *gkrSolvingData) hint.Function {
 
 	return func(_ *big.Int, ins, outs []*big.Int) error {
-		insBytes := algo_utils.Map(ins, func(i *big.Int) []byte {
+		insBytes := algo_utils.Map(ins[1:], func(i *big.Int) []byte { // the first input is dummy, just to ensure the solver's work is done before the prover is called
 			b := i.Bytes()
 			return b[:]
 		})
 
 		hsh := HashBuilderRegistry[hashName]()
 
-		solvingDone.Lock()
 		proof, err := gkr.Prove(data.circuit, data.assignments, fiatshamir.WithHash(hsh, insBytes...), gkr.WithPool(&data.memoryPool)) // TODO: Do transcriptSettings properly
 		if err != nil {
 			return err
@@ -239,10 +235,8 @@ func defineGkrHints(info constraint.GkrInfo, hintFunctions map[hint.ID]hint.Func
 		res[k] = v
 	}
 	var gkrData gkrSolvingData
-	var solvingDone sync.Mutex // if the user manages challenges correctly, the solver will see the "prove" function as dependent on the "solve" function, but better not take chances
-	solvingDone.Lock()
-	res[info.SolveHintID] = gkrSolveHint(info, &gkrData, &solvingDone)
-	res[info.ProveHintID] = gkrProveHint(info.HashName, &gkrData, &solvingDone)
+	res[info.SolveHintID] = gkrSolveHint(info, &gkrData)
+	res[info.ProveHintID] = gkrProveHint(info.HashName, &gkrData)
 	return res
 }
 
```

### std/gkr/api_test.go
```diff
@@ -97,10 +97,21 @@ func (c *sqNoDependencyCircuit) Define(api frontend.API) error {
 }
 
 func TestSqNoDependencyCircuit(t *testing.T) {
-	assignment := sqNoDependencyCircuit{X: []frontend.Variable{1, 1}}
-	circuit := sqNoDependencyCircuit{X: make([]frontend.Variable, 2)}
 
-	test.NewAssert(t).SolvingSucceeded(&circuit, &assignment, test.WithBackends(backend.GROTH16), test.WithCurves(ecc.BN254))
+	xValuess := [][]frontend.Variable{
+		{1, 1},
+		{1, 2},
+	}
+
+	hashes := []string{"-1", "-20"}
+
+	for _, xValues := range xValuess {
+		for _, hashName := range hashes {
+			assignment := sqNoDependencyCircuit{X: xValues}
+			circuit := sqNoDependencyCircuit{X: make([]frontend.Variable, len(xValues)), hashName: hashName}
+			solve(t, &circuit, &assignment)
+		}
+	}
 }
 
 type mulNoDependencyCircuit struct {
@@ -404,7 +415,7 @@ func init() {
 	//registerMessageCounter(0, 1)
 }
 
-type constHashBn254 int
+type constHashBn254 int // TODO @Tabaie move to gnark-crypto
 
 func (c constHashBn254) Write(p []byte) (int, error) {
 	return len(p), nil
```

### std/gkr/compile.go
```diff
@@ -167,8 +167,17 @@ func (s Solution) Verify(hashName string, initialChallenges ...frontend.Variable
 	forSnark := newCircuitDataForSnark(s.toStore, s.assignments)
 	logNbInstances := log2(uint(s.assignments.NbInstances()))
 
+	hintIns := make([]frontend.Variable, len(initialChallenges)+1) // hack: adding one of the outputs of the solve hint to ensure "prove" is called after "solve"
+	for i, w := range s.toStore.Circuit {
+		if w.IsOutput() {
+			hintIns[0] = s.assignments[i][0]
+			break
+		}
+	}
+	copy(hintIns[1:], initialChallenges)
+
 	if proofSerialized, err = s.parentApi.Compiler().NewHint(
-		ProveHintPlaceholder, ProofSize(forSnark.circuit, logNbInstances), initialChallenges...); err != nil {
+		ProveHintPlaceholder, ProofSize(forSnark.circuit, logNbInstances), hintIns...); err != nil {
 		return err
 	}
 	s.toStore.ProveHintID = hint.UUID(ProveHintPlaceholder)
```
