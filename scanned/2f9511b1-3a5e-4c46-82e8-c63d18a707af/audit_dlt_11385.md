# [?] fixed "attempt to subtract with overflow" issue in uni-stark (#934)

## Summary
Severity: Unknown
Chain: ZK
Component: Plonky3/Plonky3
Published: 2025-07-07
Source: https://github.com/Plonky3/Plonky3/commit/1651c3db66debae62f75e33b64f9b439b261e4dd
Type: security-commit

## Details
fixed "attempt to subtract with overflow" issue in uni-stark (#934)

## Patch
### uni-stark/src/prover.rs
```diff
@@ -9,12 +9,12 @@ use p3_field::{BasedVectorSpace, PackedValue, PrimeCharacteristicRing};
 use p3_matrix::Matrix;
 use p3_matrix::dense::RowMajorMatrix;
 use p3_maybe_rayon::prelude::*;
-use p3_util::{log2_ceil_usize, log2_strict_usize};
+use p3_util::log2_strict_usize;
 use tracing::{debug_span, info_span, instrument};
 
 use crate::{
     Commitments, Domain, OpenedValues, PackedChallenge, PackedVal, Proof, ProverConstraintFolder,
-    StarkGenericConfig, SymbolicAirBuilder, SymbolicExpression, Val, get_symbolic_constraints,
+    StarkGenericConfig, SymbolicAirBuilder, Val, get_log_quotient_degree, get_symbolic_constraints,
 };
 
 #[instrument(skip_all)]
@@ -76,16 +76,12 @@ where
     // that S_i^2 should never appear in a constraint as it should just be replaced by `S_i`.
     //
     // For now in comments we assume that `deg(C) = 3` meaning `deg(C(x)) <= 3N - 2`
-    let constraint_degree = symbolic_constraints
-        .iter()
-        .map(SymbolicExpression::degree_multiple)
-        .max()
-        .unwrap_or(0);
 
     // From the degree of the constraint polynomial, compute the number
     // of quotient polynomials we will split Q(x) into. This is chosen to
     // always be a power of 2.
-    let log_quotient_degree = log2_ceil_usize(constraint_degree - 1 + config.is_zk());
+    let log_quotient_degree =
+        get_log_quotient_degree::<Val<SC>, A>(air, 0, public_values.len(), config.is_zk());
     let quotient_degree = 1 << (log_quotient_degree + config.is_zk());
 
     // Initialize the PCS and the Challenger.
```
