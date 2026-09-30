# [?] fix: dead code removal and twiddle table race condition (#1318)

## Summary
Severity: Unknown
Chain: ZK
Component: Plonky3/Plonky3
Published: 2026-02-23
Source: https://github.com/Plonky3/Plonky3/commit/d3848b535dca49a60e368c873693360c66aff7fe
Type: security-commit

## Details
fix: dead code removal and twiddle table race condition (#1318)

## Patch
### monty-31/src/dft/mod.rs
```diff
@@ -122,14 +122,15 @@ impl<MP: FieldParameters + TwoAdicData> RecursiveDft<MontyField31<MP>> {
             })
             .collect::<Vec<_>>();
         // Helper closure to extend a table under its lock.
+        let have_minus_one = have - 1;
         let extend_table = |lock: &RwLock<Arc<[Vec<_>]>>, missing: &[Vec<_>]| {
             let mut w = lock.write();
             let current_len = w.len();
             // Double-check if an update is still needed after acquiring the write lock.
             if (current_len + 1) < need {
                 let mut v = w.to_vec();
                 // Append only the portion needed in case another thread did a partial update.
-                let extend_from = current_len.saturating_sub(current_len);
+                let extend_from = current_len.saturating_sub(have_minus_one);
                 v.extend_from_slice(&missing[extend_from..]);
                 *w = v.into();
             }
```

### poseidon2-air/src/columns.rs
```diff
@@ -70,33 +70,6 @@ pub const fn num_cols<
     )
 }
 
-pub const fn make_col_map<
-    const WIDTH: usize,
-    const SBOX_DEGREE: u64,
-    const SBOX_REGISTERS: usize,
-    const HALF_FULL_ROUNDS: usize,
-    const PARTIAL_ROUNDS: usize,
->() -> Poseidon2Cols<usize, WIDTH, SBOX_DEGREE, SBOX_REGISTERS, HALF_FULL_ROUNDS, PARTIAL_ROUNDS> {
-    todo!()
-    // let indices_arr = indices_arr::<
-    //     { num_cols::<WIDTH, SBOX_DEGREE, SBOX_REGISTERS, HALF_FULL_ROUNDS, PARTIAL_ROUNDS>() },
-    // >();
-    // unsafe {
-    //     transmute::<
-    //         [usize;
-    //             num_cols::<WIDTH, SBOX_DEGREE, SBOX_REGISTERS, HALF_FULL_ROUNDS, PARTIAL_ROUNDS>()],
-    //         Poseidon2Cols<
-    //             usize,
-    //             WIDTH,
-    //             SBOX_DEGREE,
-    //             SBOX_REGISTERS,
-    //             HALF_FULL_ROUNDS,
-    //             PARTIAL_ROUNDS,
-    //         >,
-    //     >(indices_arr)
-    // }
-}
-
 impl<
     T,
     const WIDTH: usize,
```

### rescue/Cargo.toml
```diff
@@ -15,7 +15,6 @@ p3-mds.workspace = true
 p3-symmetric.workspace = true
 p3-util.workspace = true
 
-itertools.workspace = true
 rand.workspace = true
 sha3.workspace = true
 
```

### rescue/src/rescue.rs
```diff
@@ -1,7 +1,6 @@
 use alloc::format;
 use alloc::vec::Vec;
 
-use itertools::Itertools;
 use p3_field::{Algebra, PermutationMonomial, PrimeField, PrimeField64};
 use p3_mds::MdsPermutation;
 use p3_symmetric::{CryptographicPermutation, Permutation};
@@ -96,15 +95,12 @@ where
         let byte_string = shake256_hash(seed_string.as_bytes(), num_bytes);
 
         byte_string
-            .iter()
             .chunks(bytes_per_constant)
-            .into_iter()
             .map(|chunk| {
                 let integer = chunk
-                    .collect_vec()
                     .iter()
                     .rev()
-                    .fold(0, |acc, &byte| (acc << 8) + *byte as u64);
+                    .fold(0, |acc, &byte| (acc << 8) + byte as u64);
                 F::from_u64(integer)
             })
             .collect()
```

### uni-stark/src/preprocessed.rs
```diff
@@ -1,6 +1,5 @@
 use p3_air::Air;
 use p3_commit::Pcs;
-use p3_field::Field;
 use p3_matrix::Matrix;
 use tracing::debug_span;
 
@@ -52,7 +51,6 @@ pub fn setup_preprocessed<SC, A>(
 ) -> Option<(PreprocessedProverData<SC>, PreprocessedVerifierKey<SC>)>
 where
     SC: StarkGenericConfig,
-    Val<SC>: Field,
     A: Air<SymbolicAirBuilder<Val<SC>>> + for<'a> Air<ProverConstraintFolder<'a, SC>>,
 {
     let pcs = config.pcs();
```
