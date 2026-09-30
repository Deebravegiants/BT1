# [?] Fix test stack overflows and remove unused util functions

## Summary
Severity: Unknown
Chain: ZK
Component: a16z/jolt
Published: 2025-05-02
Source: https://github.com/a16z/jolt/commit/ecd13ba791dd74dabc36f29f5df780f142883fbd
Type: security-commit

## Details
Fix test stack overflows and remove unused util functions

## Patch
### jolt-core/src/jolt/vm/instruction_lookups.rs
```diff
@@ -22,7 +22,7 @@ use crate::{
     utils::{
         errors::ProofVerifyError,
         math::Math,
-        thread::{unsafe_allocate_zero_array, unsafe_allocate_zero_vec},
+        thread::unsafe_allocate_zero_vec,
         transcript::{AppendToTranscript, Transcript},
     },
 };
@@ -285,7 +285,7 @@ fn prove_ra_booleanity<F: JoltField, ProofTranscript: Transcript>(
 
     // First log(K) rounds of sumcheck
 
-    let mut F: [F; K] = unsafe_allocate_zero_array();
+    let mut F: Vec<F> = unsafe_allocate_zero_vec(K);
     F[0] = F::one();
 
     let num_rounds = LOG_K + T.log_2();
@@ -445,30 +445,6 @@ fn prove_ra_booleanity<F: JoltField, ProofTranscript: Transcript>(
     // TODO(moodlezoup): Implement optimization from Section 6.2.2 "An optimization leveraging small memory size"
     // Last log(T) rounds of sumcheck
     for _round in 0..T.log_2() {
-        #[cfg(test)]
-        {
-            let expected: F = eq_r_r
-                * (0..H.len())
-                    .map(|j| {
-                        let D_j = D.get_bound_coeff(j);
-                        let H_j = [
-                            H[0].get_bound_coeff(j),
-                            H[1].get_bound_coeff(j),
-                            H[2].get_bound_coeff(j),
-                            H[3].get_bound_coeff(j),
-                        ];
-                        D_j * ((H_j[0].square() - H_j[0])
-                            + z * (H_j[1].square() - H_j[1])
-                            + z_squared * (H_j[2].square() - H_j[2])
-                            + z_cubed * (H_j[3].square() - H_j[3]))
-                    })
-                    .sum::<F>();
-            assert_eq!(
-                expected, previous_claim,
-                "Sumcheck sanity check failed in round {_round}"
-            );
-        }
-
         let inner_span = tracing::span!(tracing::Level::INFO, "Compute univariate poly");
         let _inner_guard = inner_span.enter();
 
@@ -642,7 +618,7 @@ fn prove_ra_hamming_weight<F: JoltField, ProofTranscript: Transcript>(
         MultilinearPolynomial::from(std::mem::take(&mut F[2])),
         MultilinearPolynomial::from(std::mem::take(&mut F[3])),
     ];
-    let mut previous_claim = F::one();
+    let mut previous_claim = F::one() + z + z_squared + z_cubed;
 
     let mut compressed_polys: Vec<CompressedUniPoly<F>> = Vec::with_capacity(num_rounds);
     for _ in 0..num_rounds {
```

### jolt-core/src/utils/thread.rs
```diff
@@ -1,4 +1,3 @@
-use rayon::prelude::*;
 use std::thread::{self, JoinHandle};
 
 use crate::field::JoltField;
@@ -66,111 +65,3 @@ pub fn unsafe_zero_slice<F: JoltField + Sized>(slice: &mut [F]) {
         std::ptr::write_bytes(slice.as_mut_ptr(), 0, slice.len());
     }
 }
-
-#[tracing::instrument(skip_all)]
-pub fn unsafe_allocate_zero_array<F: JoltField + Sized, const N: usize>() -> [F; N] {
-    #[cfg(test)]
-    {
-        // Check for safety of 0 allocation
-        unsafe {
-            let value = &F::zero();
-            let ptr = value as *const F as *const u8;
-            let bytes = std::slice::from_raw_parts(ptr, std::mem::size_of::<F>());
-            assert!(bytes.iter().all(|&byte| byte == 0));
-        }
-    }
-
-    // Bulk allocate zeros into array
-    unsafe { std::mem::zeroed() }
-}
-
-#[tracing::instrument(skip_all)]
-pub fn unsafe_allocate_sparse_zero_vec<F: JoltField + Sized>(size: usize) -> Vec<(F, usize)> {
-    // Check for safety of 0 allocation
-    unsafe {
-        let value = &F::zero();
-        let ptr = value as *const F as *const u8;
-        let bytes = std::slice::from_raw_parts(ptr, std::mem::size_of::<F>());
-        assert!(bytes.iter().all(|&byte| byte == 0));
-    }
-
-    // Bulk allocate zeros, unsafely
-    let result: Vec<(F, usize)>;
-    unsafe {
-        let layout = std::alloc::Layout::array::<(F, usize)>(size).unwrap();
-        let ptr = std::alloc::alloc_zeroed(layout) as *mut (F, usize);
-
-        if ptr.is_null() {
-            panic!("Zero vec allocation failed");
-        }
-
-        result = Vec::from_raw_parts(ptr, size, size);
-    }
-    result
-}
-
-#[tracing::instrument(skip_all)]
-pub fn par_flatten_triple<T: Send + Sync + Copy, F: Fn(usize) -> Vec<T>>(
-    triple: Vec<(Vec<T>, Vec<T>, Vec<T>)>,
-    allocate: F,
-    excess_alloc: usize,
-) -> (Vec<T>, Vec<T>, Vec<T>) {
-    let az_len: usize = triple.iter().map(|item| item.0.len()).sum();
-    let bz_len: usize = triple.iter().map(|item| item.1.len()).sum();
-    let cz_len: usize = triple.iter().map(|item| item.2.len()).sum();
-
-    let (mut a_sparse, mut b_sparse, mut c_sparse): (Vec<T>, Vec<T>, Vec<T>) =
-        (allocate(az_len), allocate(bz_len), allocate(cz_len));
-
-    let mut a_slices = Vec::with_capacity(triple.len() + excess_alloc);
-    let mut b_slices = Vec::with_capacity(triple.len() + excess_alloc);
-    let mut c_slices = Vec::with_capacity(triple.len() + excess_alloc);
-
-    let mut a_rest: &mut [T] = a_sparse.as_mut_slice();
-    let mut b_rest: &mut [T] = b_sparse.as_mut_slice();
-    let mut c_rest: &mut [T] = c_sparse.as_mut_slice();
-
-    for item in &triple {
-        let (a_chunk, a_new_rest) = a_rest.split_at_mut(item.0.len());
-        a_slices.push(a_chunk);
-        a_rest = a_new_rest;
-
-        let (b_chunk, b_new_rest) = b_rest.split_at_mut(item.1.len());
-        b_slices.push(b_chunk);
-        b_rest = b_new_rest;
-
-        let (c_chunk, c_new_rest) = c_rest.split_at_mut(item.2.len());
-        c_slices.push(c_chunk);
-        c_rest = c_new_rest;
-    }
-
-    triple
-        .into_par_iter()
-        .zip(
-            a_slices
-                .par_iter_mut()
-                .zip(b_slices.par_iter_mut().zip(c_slices.par_iter_mut())),
-        )
-        .for_each(|(chunk, (a, (b, c)))| {
-            join_triple(
-                || a.copy_from_slice(&chunk.0),
-                || b.copy_from_slice(&chunk.1),
-                || c.copy_from_slice(&chunk.2),
-            );
-        });
-
-    (a_sparse, b_sparse, c_sparse)
-}
-
-pub fn join_triple<A, B, C, RA, RB, RC>(oper_a: A, oper_b: B, oper_c: C) -> (RA, RB, RC)
-where
-    A: FnOnce() -> RA + Send,
-    B: FnOnce() -> RB + Send,
-    C: FnOnce() -> RC + Send,
-    RA: Send,
-    RB: Send,
-    RC: Send,
-{
-    let (res_a, (res_b, res_c)) = rayon::join(oper_a, || rayon::join(oper_b, oper_c));
-    (res_a, res_b, res_c)
-}
```
