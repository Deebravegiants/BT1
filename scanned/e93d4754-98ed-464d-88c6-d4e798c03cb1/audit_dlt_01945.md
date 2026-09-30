# [?] fixed race condition in the prepareWitnesses function: before the fix, goroutine used to change numEffWitnesses but the top-level method did not wait 

## Summary
Severity: Unknown
Chain: Linea
Component: Consensys/linea-monorepo
Published: 2025-05-06
Source: https://github.com/LFDT-Lineth/lineth-monorepo/commit/3bede19e492619f65978ec162c2b301befeaecf8
Type: security-commit

## Details
fixed race condition in the prepareWitnesses function: before the fix, goroutine used to change numEffWitnesses but the top-level method did not wait for goroutine to complete, that caused the usage of the numEffWitnesses before it change in the other methods (#939)

## Patch
### prover/protocol/dedicated/plonk/alignment.go
```diff
@@ -134,7 +134,7 @@ func (ci *CircuitAlignmentInput) prepareWitnesses(run *wizard.ProverRuntime) {
 				return ci.witnesses[ii].Fill(ci.nbPublicInputs, 0, witnessFillers[ii])
 			})
 		}
-		go func() {
+		wg.Go(func() error {
 			var filled int
 			for j := 0; j < dataCol.Len(); j++ {
 				mask := maskCol.Get(j)
@@ -144,7 +144,7 @@ func (ci *CircuitAlignmentInput) prepareWitnesses(run *wizard.ProverRuntime) {
 				data := dataCol.Get(j)
 				select {
 				case <-ctx.Done():
-					return
+					return nil
 				case witnessFillers[filled/ci.nbPublicInputs] <- data:
 				}
 				filled++
@@ -160,15 +160,17 @@ func (ci *CircuitAlignmentInput) prepareWitnesses(run *wizard.ProverRuntime) {
 			for filled < ci.nbPublicInputs*ci.NbCircuitInstances {
 				select {
 				case <-ctx.Done():
-					return
+					return nil
 				case witnessFillers[filled/ci.nbPublicInputs] <- ci.InputFiller(filled/ci.nbPublicInputs, filled%ci.nbPublicInputs):
 				}
 				filled++
 				if filled%ci.nbPublicInputs == 0 {
 					close(witnessFillers[(filled-1)/ci.nbPublicInputs])
 				}
 			}
-		}()
+
+			return nil
+		})
 		if err := wg.Wait(); err != nil {
 			utils.Panic("fill witness: %v", err.Error())
 			return
```
