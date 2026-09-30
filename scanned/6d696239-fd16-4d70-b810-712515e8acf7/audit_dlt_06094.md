# [?] fix(ec): rayon::ThreadPoolBuilder panic in wasm32 (#1112)

## Summary
Severity: Unknown
Chain: ZK
Component: arkworks-rs/algebra
Published: 2026-06-20
Source: https://github.com/arkworks-rs/algebra/commit/d7f73154500ee45e52d87d43ca3584ad3f2072d4
Type: security-commit

## Details
fix(ec): rayon::ThreadPoolBuilder panic in wasm32 (#1112)

* fix(ec): rayon::ThreadPoolBuilder panic in wasm32

* chore: update CHANGELOG.md

* lint: style

* chore: fix changelog typo

---------

Co-authored-by: weikengchen <w.k@berkeley.edu>

## Patch
### CHANGELOG.md
```diff
@@ -14,6 +14,7 @@
 - [\#1039](https://github.com/arkworks-rs/algebra/pull/1039) (`ark-ff-asm`) Remove unused dead spill buffer path.
 - [\#1044](https://github.com/arkworks-rs/algebra/pull/1044), [\#1084](https://github.com/arkworks-rs/algebra/pull/1084), [\#1088](https://github.com/arkworks-rs/algebra/pull/1088) Add implementation for small field with native integer types
 - [\#1061](https://github.com/arkworks-rs/algebra/pull/1061) (`ark-poly`) Reduce allocations in `DenseMultilinearExtension::{concat, fix_variables, evaluate}`.
+- [\#1112](https://github.com/arkworks-rs/algebra/pull/1112) (`ark-ec`) Fix rayon::ThreadPoolBuilder panicking in wasm32 when parallel feature is enabled
 
 ### Breaking changes
 
```

### ec/src/scalar_mul/variable_base/mod.rs
```diff
@@ -542,14 +542,15 @@ fn msm_bigint_wnaf<V: VariableBaseMSM>(
     cfg_chunks!(bases, chunk_size)
         .zip(cfg_chunks!(scalars, chunk_size))
         .map(|(bases, scalars)| {
-            #[cfg(feature = "parallel")]
+            // wasm32 can't spawn OS threads
+            #[cfg(all(feature = "parallel", not(target_arch = "wasm32")))]
             let result = rayon::ThreadPoolBuilder::new()
                 .num_threads(THREADS_PER_CHUNK.min(rayon::current_num_threads()))
                 .build()
                 .unwrap()
                 .install(|| msm_bigint_wnaf_parallel::<V>(bases, scalars));
 
-            #[cfg(not(feature = "parallel"))]
+            #[cfg(any(not(feature = "parallel"), target_arch = "wasm32"))]
             let result = msm_bigint_wnaf_parallel::<V>(bases, scalars);
 
             result
```
