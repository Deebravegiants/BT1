# [?] Prevent addition overflow

## Summary
Severity: Unknown
Chain: Aleo
Component: AleoNet/snarkVM-test
Published: 2023-09-13
Source: https://github.com/AleoNet/snarkVM-test/commit/bf5619bda80c41b8355d03cdc7686ee214457688
Type: security-commit

## Details
Prevent addition overflow

## Patch
### algorithms/src/snark/varuna/ahp/indexer/circuit.rs
```diff
@@ -169,15 +169,14 @@ impl<F: PrimeField, MM: SNARKMode> CanonicalSerialize for Circuit<F, MM> {
 
     #[allow(unused_mut, unused_variables)]
     fn serialized_size(&self, mode: Compress) -> usize {
-        let mut size = 0;
-        size += self.index_info.serialized_size(mode);
-        size += self.a.serialized_size(mode);
-        size += self.b.serialized_size(mode);
-        size += self.c.serialized_size(mode);
-        size += self.a_arith.serialized_size(mode);
-        size += self.b_arith.serialized_size(mode);
-        size += self.c_arith.serialized_size(mode);
-        size
+        0usize
+            .saturating_add(self.index_info.serialized_size(mode))
+            .saturating_add(self.a.serialized_size(mode))
+            .saturating_add(self.b.serialized_size(mode))
+            .saturating_add(self.c.serialized_size(mode))
+            .saturating_add(self.a_arith.serialized_size(mode))
+            .saturating_add(self.b_arith.serialized_size(mode))
+            .saturating_add(self.c_arith.serialized_size(mode))
     }
 }
 
```

### algorithms/src/snark/varuna/ahp/prover/state.rs
```diff
@@ -104,7 +104,7 @@ impl<'a, F: PrimeField, MM: SNARKMode> State<'a, F, MM> {
         let mut max_non_zero_domain: Option<EvaluationDomain<F>> = None;
         let mut max_num_constraints = 0;
         let mut max_num_variables = 0;
-        let mut total_instances = 0;
+        let mut total_instances = 0usize;
         let circuit_specific_states = indices_and_assignments
             .into_iter()
             .map(|(circuit, variable_assignments)| {
@@ -124,7 +124,8 @@ impl<'a, F: PrimeField, MM: SNARKMode> State<'a, F, MM> {
                 let first_padded_public_inputs = &variable_assignments[0].0;
                 let input_domain = EvaluationDomain::new(first_padded_public_inputs.len()).unwrap();
                 let batch_size = variable_assignments.len();
-                total_instances += batch_size;
+                total_instances =
+                    total_instances.checked_add(batch_size).ok_or_else(|| anyhow::anyhow!("Batch size too large"))?;
                 let mut z_as = Vec::with_capacity(batch_size);
                 let mut z_bs = Vec::with_capacity(batch_size);
                 let mut z_cs = Vec::with_capacity(batch_size);
```

### algorithms/src/snark/varuna/data_structures/proof.rs
```diff
@@ -71,17 +71,15 @@ impl<E: PairingEngine> Commitments<E> {
     }
 
     fn serialized_size(&self, compress: Compress) -> usize {
-        let mut size = 0;
-        size += serialized_vec_size_without_len(&self.witness_commitments, compress);
-        size += CanonicalSerialize::serialized_size(&self.mask_poly, compress);
-        size += CanonicalSerialize::serialized_size(&self.h_0, compress);
-        size += CanonicalSerialize::serialized_size(&self.g_1, compress);
-        size += CanonicalSerialize::serialized_size(&self.h_1, compress);
-        size += serialized_vec_size_without_len(&self.g_a_commitments, compress);
-        size += serialized_vec_size_without_len(&self.g_b_commitments, compress);
-        size += serialized_vec_size_without_len(&self.g_c_commitments, compress);
-        size += CanonicalSerialize::serialized_size(&self.h_2, compress);
-        size
+        serialized_vec_size_without_len(&self.witness_commitments, compress)
+            .saturating_add(CanonicalSerialize::serialized_size(&self.mask_poly, compress))
+            .saturating_add(CanonicalSerialize::serialized_size(&self.h_0, compress))
+            .saturating_add(CanonicalSerialize::serialized_size(&self.g_1, compress))
+            .saturating_add(CanonicalSerialize::serialized_size(&self.h_1, compress))
+            .saturating_add(serialized_vec_size_without_len(&self.g_a_commitments, compress))
+            .saturating_add(serialized_vec_size_without_len(&self.g_b_commitments, compress))
+            .saturating_add(serialized_vec_size_without_len(&self.g_c_commitments, compress))
+            .saturating_add(CanonicalSerialize::serialized_size(&self.h_2, compress))
     }
 
     fn deserialize_with_mode<R: snarkvm_utilities::Read>(
@@ -140,12 +138,10 @@ impl<F: PrimeField> Evaluations<F> {
     }
 
     fn serialized_size(&self, compress: Compress) -> usize {
-        let mut size = 0;
-        size += CanonicalSerialize::serialized_size(&self.g_1_eval, compress);
-        size += serialized_vec_size_without_len(&self.g_a_evals, compress);
-        size += serialized_vec_size_without_len(&self.g_b_evals, compress);
-        size += serialized_vec_size_without_len(&self.g_c_evals, compress);
-        size
+        CanonicalSerialize::serialized_size(&self.g_1_eval, compress)
+            .saturating_add(serialized_vec_size_without_len(&self.g_a_evals, compress))
+            .saturating_add(serialized_vec_size_without_len(&self.g_b_evals, compress))
+            .saturating_add(serialized_vec_size_without_len(&self.g_c_evals, compress))
     }
 
     fn deserialize_with_mode<R: snarkvm_utilities::Read>(
```

### algorithms/src/snark/varuna/varuna.rs
```diff
@@ -358,7 +358,7 @@ where
         let mut batch_sizes = BTreeMap::new();
         let mut circuit_infos = BTreeMap::new();
         let mut inputs_and_batch_sizes = BTreeMap::new();
-        let mut total_instances = 0;
+        let mut total_instances = 0usize;
         let mut public_inputs = BTreeMap::new(); // inputs need to live longer than the rest of prover_state
         let num_unique_circuits = keys_to_constraints.len();
         let mut circuit_ids = Vec::with_capacity(num_unique_circuits);
@@ -371,8 +371,9 @@ where
             batch_sizes.insert(circuit_id, batch_size);
             circuit_infos.insert(circuit_id, &pk.circuit_verifying_key.circuit_info);
             inputs_and_batch_sizes.insert(circuit_id, (batch_size, padded_public_input));
-            total_instances += batch_size;
             public_inputs.insert(circuit_id, public_input);
+            total_instances = total_instances.saturating_add(batch_size);
+
             circuit_ids.push(circuit_id);
         }
         assert_eq!(prover_state.total_instances, total_instances);
```
