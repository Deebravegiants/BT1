# [?] fix: plonk build permutation index out of bounds

## Summary
Severity: Unknown
Chain: ZK
Component: Consensys-Incorporated/gnark
Published: 2021-10-20
Source: https://github.com/Consensys-Incorporated/gnark/commit/817df3f0e04c22fdcccead98aec0f1b13f301104
Type: security-commit

## Details
fix: plonk build permutation index out of bounds

## Patch
### internal/backend/bls12-377/plonk/setup.go
```diff
@@ -210,66 +210,50 @@ func Setup(spr *cs.SparseR1CS, srs *kzg.SRS) (*ProvingKey, *VerifyingKey, error)
 // like this: for i in tab: tab[i] = tab[permutation[i]]
 func buildPermutation(spr *cs.SparseR1CS, pk *ProvingKey) {
 
+	nbVariables := spr.NbInternalVariables + spr.NbPublicVariables + spr.NbSecretVariables
 	sizeSolution := int(pk.DomainNum.Cardinality)
 
-	// position -> variable_ID
-	lro := make([]int, 3*sizeSolution)
-
+	// init permutation
 	pk.Permutation = make([]int64, 3*sizeSolution)
-	for i := 0; i < spr.NbPublicVariables; i++ { // IDs of LRO associated to placeholders (only L needs to be taken care of)
-
-		lro[i] = i
-		lro[sizeSolution+i] = 0
-		lro[2*sizeSolution+i] = 0
-
+	for i := 0; i < len(pk.Permutation); i++ {
 		pk.Permutation[i] = -1
-		pk.Permutation[sizeSolution+i] = -1
-		pk.Permutation[2*sizeSolution+i] = -1
 	}
+
+	// init LRO position -> variable_ID
+	lro := make([]int, 3*sizeSolution) // position -> variable_ID
+	for i := 0; i < spr.NbPublicVariables; i++ {
+		lro[i] = i // IDs of LRO associated to placeholders (only L needs to be taken care of)
+	}
+
 	offset := spr.NbPublicVariables
 	for i := 0; i < len(spr.Constraints); i++ { // IDs of LRO associated to constraints
-
 		lro[offset+i] = spr.Constraints[i].L.VariableID()
 		lro[sizeSolution+offset+i] = spr.Constraints[i].R.VariableID()
 		lro[2*sizeSolution+offset+i] = spr.Constraints[i].O.VariableID()
-
-		pk.Permutation[i+offset] = -1
-		pk.Permutation[sizeSolution+i+offset] = -1
-		pk.Permutation[2*sizeSolution+i+offset] = -1
-	}
-	offset += len(spr.Constraints)
-
-	for i := 0; i < sizeSolution-offset; i++ {
-
-		pk.Permutation[offset+i] = -1
-		pk.Permutation[offset+sizeSolution+i] = -1
-		pk.Permutation[offset+2*sizeSolution+i] = -1
 	}
 
-	nbVariables := spr.NbInternalVariables + spr.NbPublicVariables + spr.NbSecretVariables
-
+	// init cycle:
 	// map ID -> last position the ID was seen
 	cycle := make([]int64, nbVariables)
 	for i := 0; i < len(cycle); i++ {
 		cycle[i] = -1
 	}
 
-	for i := 0; i < 3*sizeSolution; i++ {
+	for i := 0; i < len(lro); i++ {
 		if cycle[lro[i]] != -1 {
+			// if != -1, it means we already encountered this value
+			// so we need to set the corresponding permutation index.
 			pk.Permutation[i] = cycle[lro[i]]
 		}
 		cycle[lro[i]] = int64(i)
 	}
 
 	// complete the Permutation by filling the first IDs encountered
-	counter := nbVariables
-	for iter := 0; counter > 0; iter++ {
-		if pk.Permutation[iter] == -1 {
-			pk.Permutation[iter] = cycle[lro[iter]]
-			counter--
+	for i := 0; i < len(pk.Permutation); i++ {
+		if pk.Permutation[i] == -1 {
+			pk.Permutation[i] = cycle[lro[i]]
 		}
 	}
-
 }
 
 // computeLDE computes the LDE (Lagrange basis) of the permutations
```

### internal/backend/bls12-381/plonk/setup.go
```diff
@@ -210,66 +210,50 @@ func Setup(spr *cs.SparseR1CS, srs *kzg.SRS) (*ProvingKey, *VerifyingKey, error)
 // like this: for i in tab: tab[i] = tab[permutation[i]]
 func buildPermutation(spr *cs.SparseR1CS, pk *ProvingKey) {
 
+	nbVariables := spr.NbInternalVariables + spr.NbPublicVariables + spr.NbSecretVariables
 	sizeSolution := int(pk.DomainNum.Cardinality)
 
-	// position -> variable_ID
-	lro := make([]int, 3*sizeSolution)
-
+	// init permutation
 	pk.Permutation = make([]int64, 3*sizeSolution)
-	for i := 0; i < spr.NbPublicVariables; i++ { // IDs of LRO associated to placeholders (only L needs to be taken care of)
-
-		lro[i] = i
-		lro[sizeSolution+i] = 0
-		lro[2*sizeSolution+i] = 0
-
+	for i := 0; i < len(pk.Permutation); i++ {
 		pk.Permutation[i] = -1
-		pk.Permutation[sizeSolution+i] = -1
-		pk.Permutation[2*sizeSolution+i] = -1
 	}
+
+	// init LRO position -> variable_ID
+	lro := make([]int, 3*sizeSolution) // position -> variable_ID
+	for i := 0; i < spr.NbPublicVariables; i++ {
+		lro[i] = i // IDs of LRO associated to placeholders (only L needs to be taken care of)
+	}
+
 	offset := spr.NbPublicVariables
 	for i := 0; i < len(spr.Constraints); i++ { // IDs of LRO associated to constraints
-
 		lro[offset+i] = spr.Constraints[i].L.VariableID()
 		lro[sizeSolution+offset+i] = spr.Constraints[i].R.VariableID()
 		lro[2*sizeSolution+offset+i] = spr.Constraints[i].O.VariableID()
-
-		pk.Permutation[i+offset] = -1
-		pk.Permutation[sizeSolution+i+offset] = -1
-		pk.Permutation[2*sizeSolution+i+offset] = -1
-	}
-	offset += len(spr.Constraints)
-
-	for i := 0; i < sizeSolution-offset; i++ {
-
-		pk.Permutation[offset+i] = -1
-		pk.Permutation[offset+sizeSolution+i] = -1
-		pk.Permutation[offset+2*sizeSolution+i] = -1
 	}
 
-	nbVariables := spr.NbInternalVariables + spr.NbPublicVariables + spr.NbSecretVariables
-
+	// init cycle:
 	// map ID -> last position the ID was seen
 	cycle := make([]int64, nbVariables)
 	for i := 0; i < len(cycle); i++ {
 		cycle[i] = -1
 	}
 
-	for i := 0; i < 3*sizeSolution; i++ {
+	for i := 0; i < len(lro); i++ {
 		if cycle[lro[i]] != -1 {
+			// if != -1, it means we already encountered this value
+			// so we need to set the corresponding permutation index.
 			pk.Permutation[i] = cycle[lro[i]]
 		}
 		cycle[lro[i]] = int64(i)
 	}
 
 	// complete the Permutation by filling the first IDs encountered
-	counter := nbVariables
-	for iter := 0; counter > 0; iter++ {
-		if pk.Permutation[iter] == -1 {
-			pk.Permutation[iter] = cycle[lro[iter]]
-			counter--
+	for i := 0; i < len(pk.Permutation); i++ {
+		if pk.Permutation[i] == -1 {
+			pk.Permutation[i] = cycle[lro[i]]
 		}
 	}
-
 }
 
 // computeLDE computes the LDE (Lagrange basis) of the permutations
```

### internal/backend/bls24-315/plonk/setup.go
```diff
@@ -210,66 +210,50 @@ func Setup(spr *cs.SparseR1CS, srs *kzg.SRS) (*ProvingKey, *VerifyingKey, error)
 // like this: for i in tab: tab[i] = tab[permutation[i]]
 func buildPermutation(spr *cs.SparseR1CS, pk *ProvingKey) {
 
+	nbVariables := spr.NbInternalVariables + spr.NbPublicVariables + spr.NbSecretVariables
 	sizeSolution := int(pk.DomainNum.Cardinality)
 
-	// position -> variable_ID
-	lro := make([]int, 3*sizeSolution)
-
+	// init permutation
 	pk.Permutation = make([]int64, 3*sizeSolution)
-	for i := 0; i < spr.NbPublicVariables; i++ { // IDs of LRO associated to placeholders (only L needs to be taken care of)
-
-		lro[i] = i
-		lro[sizeSolution+i] = 0
-		lro[2*sizeSolution+i] = 0
-
+	for i := 0; i < len(pk.Permutation); i++ {
 		pk.Permutation[i] = -1
-		pk.Permutation[sizeSolution+i] = -1
-		pk.Permutation[2*sizeSolution+i] = -1
 	}
+
+	// init LRO position -> variable_ID
+	lro := make([]int, 3*sizeSolution) // position -> variable_ID
+	for i := 0; i < spr.NbPublicVariables; i++ {
+		lro[i] = i // IDs of LRO associated to placeholders (only L needs to be taken care of)
+	}
+
 	offset := spr.NbPublicVariables
 	for i := 0; i < len(spr.Constraints); i++ { // IDs of LRO associated to constraints
-
 		lro[offset+i] = spr.Constraints[i].L.VariableID()
 		lro[sizeSolution+offset+i] = spr.Constraints[i].R.VariableID()
 		lro[2*sizeSolution+offset+i] = spr.Constraints[i].O.VariableID()
-
-		pk.Permutation[i+offset] = -1
-		pk.Permutation[sizeSolution+i+offset] = -1
-		pk.Permutation[2*sizeSolution+i+offset] = -1
-	}
-	offset += len(spr.Constraints)
-
-	for i := 0; i < sizeSolution-offset; i++ {
-
-		pk.Permutation[offset+i] = -1
-		pk.Permutation[offset+sizeSolution+i] = -1
-		pk.Permutation[offset+2*sizeSolution+i] = -1
 	}
 
-	nbVariables := spr.NbInternalVariables + spr.NbPublicVariables + spr.NbSecretVariables
-
+	// init cycle:
 	// map ID -> last position the ID was seen
 	cycle := make([]int64, nbVariables)
 	for i := 0; i < len(cycle); i++ {
 		cycle[i] = -1
 	}
 
-	for i := 0; i < 3*sizeSolution; i++ {
+	for i := 0; i < len(lro); i++ {
 		if cycle[lro[i]] != -1 {
+			// if != -1, it means we already encountered this value
+			// so we need to set the corresponding permutation index.
 			pk.Permutation[i] = cycle[lro[i]]
 		}
 		cycle[lro[i]] = int64(i)
 	}
 
 	// complete the Permutation by filling the first IDs encountered
-	counter := nbVariables
-	for iter := 0; counter > 0; iter++ {
-		if pk.Permutation[iter] == -1 {
-			pk.Permutation[iter] = cycle[lro[iter]]
-			counter--
+	for i := 0; i < len(pk.Permutation); i++ {
+		if pk.Permutation[i] == -1 {
+			pk.Permutation[i] = cycle[lro[i]]
 		}
 	}
-
 }
 
 // computeLDE computes the LDE (Lagrange basis) of the permutations
```

### internal/backend/bn254/plonk/setup.go
```diff
@@ -210,66 +210,50 @@ func Setup(spr *cs.SparseR1CS, srs *kzg.SRS) (*ProvingKey, *VerifyingKey, error)
 // like this: for i in tab: tab[i] = tab[permutation[i]]
 func buildPermutation(spr *cs.SparseR1CS, pk *ProvingKey) {
 
+	nbVariables := spr.NbInternalVariables + spr.NbPublicVariables + spr.NbSecretVariables
 	sizeSolution := int(pk.DomainNum.Cardinality)
 
-	// position -> variable_ID
-	lro := make([]int, 3*sizeSolution)
-
+	// init permutation
 	pk.Permutation = make([]int64, 3*sizeSolution)
-	for i := 0; i < spr.NbPublicVariables; i++ { // IDs of LRO associated to placeholders (only L needs to be taken care of)
-
-		lro[i] = i
-		lro[sizeSolution+i] = 0
-		lro[2*sizeSolution+i] = 0
-
+	for i := 0; i < len(pk.Permutation); i++ {
 		pk.Permutation[i] = -1
-		pk.Permutation[sizeSolution+i] = -1
-		pk.Permutation[2*sizeSolution+i] = -1
 	}
+
+	// init LRO position -> variable_ID
+	lro := make([]int, 3*sizeSolution) // position -> variable_ID
+	for i := 0; i < spr.NbPublicVariables; i++ {
+		lro[i] = i // IDs of LRO associated to placeholders (only L needs to be taken care of)
+	}
+
 	offset := spr.NbPublicVariables
 	for i := 0; i < len(spr.Constraints); i++ { // IDs of LRO associated to constraints
-
 		lro[offset+i] = spr.Constraints[i].L.VariableID()
 		lro[sizeSolution+offset+i] = spr.Constraints[i].R.VariableID()
 		lro[2*sizeSolution+offset+i] = spr.Constraints[i].O.VariableID()
-
-		pk.Permutation[i+offset] = -1
-		pk.Permutation[sizeSolution+i+offset] = -1
-		pk.Permutation[2*sizeSolution+i+offset] = -1
-	}
-	offset += len(spr.Constraints)
-
-	for i := 0; i < sizeSolution-offset; i++ {
-
-		pk.Permutation[offset+i] = -1
-		pk.Permutation[offset+sizeSolution+i] = -1
-		pk.Permutation[offset+2*sizeSolution+i] = -1
 	}
 
-	nbVariables := spr.NbInternalVariables + spr.NbPublicVariables + spr.NbSecretVariables
-
+	// init cycle:
 	// map ID -> last position the ID was seen
 	cycle := make([]int64, nbVariables)
 	for i := 0; i < len(cycle); i++ {
 		cycle[i] = -1
 	}
 
-	for i := 0; i < 3*sizeSolution; i++ {
+	for i := 0; i < len(lro); i++ {
 		if cycle[lro[i]] != -1 {
+			// if != -1, it means we already encountered this value
+			// so we need to set the corresponding permutation index.
 			pk.Permutation[i] = cycle[lro[i]]
 		}
 		cycle[lro[i]] = int64(i)
 	}
 
 	// complete the Permutation by filling the first IDs encountered
-	counter := nbVariables
-	for iter := 0; counter > 0; iter++ {
-		if pk.Permutation[iter] == -1 {
-			pk.Permutation[iter] = cycle[lro[iter]]
-			counter--
+	for i := 0; i < len(pk.Permutation); i++ {
+		if pk.Permutation[i] == -1 {
+			pk.Permutation[i] = cycle[lro[i]]
 		}
 	}
-
 }
 
 // computeLDE computes the LDE (Lagrange basis) of the permutations
```

### internal/backend/bw6-761/plonk/setup.go
```diff
@@ -210,66 +210,50 @@ func Setup(spr *cs.SparseR1CS, srs *kzg.SRS) (*ProvingKey, *VerifyingKey, error)
 // like this: for i in tab: tab[i] = tab[permutation[i]]
 func buildPermutation(spr *cs.SparseR1CS, pk *ProvingKey) {
 
+	nbVariables := spr.NbInternalVariables + spr.NbPublicVariables + spr.NbSecretVariables
 	sizeSolution := int(pk.DomainNum.Cardinality)
 
-	// position -> variable_ID
-	lro := make([]int, 3*sizeSolution)
-
+	// init permutation
 	pk.Permutation = make([]int64, 3*sizeSolution)
-	for i := 0; i < spr.NbPublicVariables; i++ { // IDs of LRO associated to placeholders (only L needs to be taken care of)
-
-		lro[i] = i
-		lro[sizeSolution+i] = 0
-		lro[2*sizeSolution+i] = 0
-
+	for i := 0; i < len(pk.Permutation); i++ {
 		pk.Permutation[i] = -1
-		pk.Permutation[sizeSolution+i] = -1
-		pk.Permutation[2*sizeSolution+i] = -1
 	}
+
+	// init LRO position -> variable_ID
+	lro := make([]int, 3*sizeSolution) // position -> variable_ID
+	for i := 0; i < spr.NbPublicVariables; i++ {
+		lro[i] = i // IDs of LRO associated to placeholders (only L needs to be taken care of)
+	}
+
 	offset := spr.NbPublicVariables
 	for i := 0; i < len(spr.Constraints); i++ { // IDs of LRO associated to constraints
-
 		lro[offset+i] = spr.Constraints[i].L.VariableID()
 		lro[sizeSolution+offset+i] = spr.Constraints[i].R.VariableID()
 		lro[2*sizeSolution+offset+i] = spr.Constraints[i].O.VariableID()
-
-		pk.Permutation[i+offset] = -1
-		pk.Permutation[sizeSolution+i+offset] = -1
-		pk.Permutation[2*sizeSolution+i+offset] = -1
-	}
-	offset += len(spr.Constraints)
-
-	for i := 0; i < sizeSolution-offset; i++ {
-
-		pk.Permutation[offset+i] = -1
-		pk.Permutation[offset+sizeSolution+i] = -1
-		pk.Permutation[offset+2*sizeSolution+i] = -1
 	}
 
-	nbVariables := spr.NbInternalVariables + spr.NbPublicVariables + spr.NbSecretVariables
-
+	// init cycle:
 	// map ID -> last position the ID was seen
 	cycle := make([]int64, nbVariables)
 	for i := 0; i < len(cycle); i++ {
 		cycle[i] = -1
 	}
 
-	for i := 0; i < 3*sizeSolution; i++ {
+	for i := 0; i < len(lro); i++ {
 		if cycle[lro[i]] != -1 {
+			// if != -1, it means we already encountered this value
+			// so we need to set the corresponding permutation index.
 			pk.Permutation[i] = cycle[lro[i]]
 		}
 		cycle[lro[i]] = int64(i)
 	}
 
 	// complete the Permutation by filling the first IDs encountered
-	counter := nbVariables
-	for iter := 0; counter > 0; iter++ {
-		if pk.Permutation[iter] == -1 {
-			pk.Permutation[iter] = cycle[lro[iter]]
-			counter--
+	for i := 0; i < len(pk.Permutation); i++ {
+		if pk.Permutation[i] == -1 {
+			pk.Permutation[i] = cycle[lro[i]]
 		}
 	}
-
 }
 
 // computeLDE computes the LDE (Lagrange basis) of the permutations
```

### internal/generator/backend/template/zkpschemes/plonk/plonk.setup.go.tmpl
```diff
@@ -192,66 +192,50 @@ func Setup(spr *cs.SparseR1CS, srs *kzg.SRS) (*ProvingKey, *VerifyingKey, error)
 // like this: for i in tab: tab[i] = tab[permutation[i]]
 func buildPermutation(spr *cs.SparseR1CS, pk *ProvingKey) {
 
+	nbVariables := spr.NbInternalVariables + spr.NbPublicVariables + spr.NbSecretVariables
 	sizeSolution := int(pk.DomainNum.Cardinality)
 
-	// position -> variable_ID
-	lro := make([]int, 3*sizeSolution)
-
+	// init permutation
 	pk.Permutation = make([]int64, 3*sizeSolution)
-	for i := 0; i < spr.NbPublicVariables; i++ { // IDs of LRO associated to placeholders (only L needs to be taken care of)
-
-		lro[i] = i
-		lro[sizeSolution+i] = 0
-		lro[2*sizeSolution+i] = 0
-
+	for i := 0; i < len(pk.Permutation); i++ {
 		pk.Permutation[i] = -1
-		pk.Permutation[sizeSolution+i] = -1
-		pk.Permutation[2*sizeSolution+i] = -1
 	}
+
+	// init LRO position -> variable_ID
+	lro := make([]int, 3*sizeSolution) // position -> variable_ID
+	for i := 0; i < spr.NbPublicVariables; i++ {
+		lro[i] = i // IDs of LRO associated to placeholders (only L needs to be taken care of)
+	}
+
 	offset := spr.NbPublicVariables
 	for i := 0; i < len(spr.Constraints); i++ { // IDs of LRO associated to constraints
-
 		lro[offset+i] = spr.Constraints[i].L.VariableID()
 		lro[sizeSolution+offset+i] = spr.Constraints[i].R.VariableID()
 		lro[2*sizeSolution+offset+i] = spr.Constraints[i].O.VariableID()
-
-		pk.Permutation[i+offset] = -1
-		pk.Permutation[sizeSolution+i+offset] = -1
-		pk.Permutation[2*sizeSolution+i+offset] = -1
-	}
-	offset += len(spr.Constraints)
-
-	for i := 0; i < sizeSolution-offset; i++ {
-
-		pk.Permutation[offset+i] = -1
-		pk.Permutation[offset+sizeSolution+i] = -1
-		pk.Permutation[offset+2*sizeSolution+i] = -1
 	}
 
-	nbVariables := spr.NbInternalVariables + spr.NbPublicVariables + spr.NbSecretVariables
-
+	// init cycle:
 	// map ID -> last position the ID was seen
 	cycle := make([]int64, nbVariables)
 	for i := 0; i < len(cycle); i++ {
 		cycle[i] = -1
 	}
 
-	for i := 0; i < 3*sizeSolution; i++ {
+	for i := 0; i < len(lro); i++ {
 		if cycle[lro[i]] != -1 {
+			// if != -1, it means we already encountered this value
+			// so we need to set the corresponding permutation index.
 			pk.Permutation[i] = cycle[lro[i]]
 		}
 		cycle[lro[i]] = int64(i)
 	}
 
 	// complete the Permutation by filling the first IDs encountered
-	counter := nbVariables
-	for iter := 0; counter > 0; iter++ {
-		if pk.Permutation[iter] == -1 {
-			pk.Permutation[iter] = cycle[lro[iter]]
-			counter--
+	for i := 0; i < len(pk.Permutation); i++ {
+		if pk.Permutation[i] == -1 {
+			pk.Permutation[i] = cycle[lro[i]]
 		}
 	}
-
 }
 
 // computeLDE computes the LDE (Lagrange basis) of the permutations
```
