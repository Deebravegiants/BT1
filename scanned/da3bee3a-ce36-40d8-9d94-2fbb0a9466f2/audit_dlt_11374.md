# [?] fix(whir): error instead of panic on invalid per-round folding schedule (#1741)

## Summary
Severity: Unknown
Chain: ZK
Component: Plonky3/Plonky3
Published: 2026-06-07
Source: https://github.com/Plonky3/Plonky3/commit/7ad1c0c7fb16e72f3584f2ca73bc9d7a5c6aa105
Type: security-commit

## Details
fix(whir): error instead of panic on invalid per-round folding schedule (#1741)

`FoldingFactor::compute_number_of_rounds` panicked when an explicit
`PerRound` schedule did not fold the polynomial down to the
direct-send threshold, and could underflow `remaining` when a round
folded more variables than were left.

Make the function return `Result<(usize, usize), FoldingFactorError>`:
- under-folding now yields a new `InsufficientFolding` variant,
- over-folding a round yields `TooLarge` (closing the latent underflow).

`WhirConfig::new` propagates it via `?` (already `From<FoldingFactorError>`).
The `empty_proof` path no longer recomputes the schedule from raw
parameters: `WhirProof::empty` now takes the round and query counts
the validated config already holds, so that path is infallible by
construction with no `expect` at the trait boundary.

Co-authored-by: Claude Opus 4.8 (1M context) <noreply@anthropic.com>

## Patch
### whir/benches/fri_vs_whir.rs
```diff
@@ -248,7 +248,9 @@ type WhirCommitTy<MT> = <MT as Mmcs<F>>::Commitment;
 /// - Each round adds the count of variables it folds away, minus one.
 fn default_round_log_inv_rates(num_variables: usize, folding_factor: &FoldingFactor) -> Vec<usize> {
     // One entry per intermediate round; the trailing direct-send round has no entry.
-    let (num_rounds, _) = folding_factor.compute_number_of_rounds(num_variables);
+    let (num_rounds, _) = folding_factor
+        .compute_number_of_rounds(num_variables)
+        .expect("valid folding schedule");
     let mut rates = Vec::with_capacity(num_rounds);
     // Start at the base rate of the first committed codeword.
     let mut rate = 1;
```

### whir/benches/whir_pcs.rs
```diff
@@ -99,7 +99,9 @@ impl Options {
 /// round. Round 0 starts at rate 1 and each subsequent round absorbs one fewer
 /// rate halving per folded variable.
 fn default_round_log_inv_rates(num_variables: usize, folding_factor: &FoldingFactor) -> Vec<usize> {
-    let (num_rounds, _) = folding_factor.compute_number_of_rounds(num_variables);
+    let (num_rounds, _) = folding_factor
+        .compute_number_of_rounds(num_variables)
+        .expect("valid folding schedule");
     let mut rates = Vec::with_capacity(num_rounds);
     let mut rate = 1;
     for round in 0..num_rounds {
```

### whir/examples/whir.rs
```diff
@@ -138,7 +138,9 @@ fn main() {
     let mmcs = MyMmcs::new(merkle_hash, merkle_compress, 0);
 
     let round_log_inv_rates = if args.round_log_inv_rates.is_empty() {
-        let (num_rounds, _) = folding_factor.compute_number_of_rounds(num_variables);
+        let (num_rounds, _) = folding_factor
+            .compute_number_of_rounds(num_variables)
+            .expect("valid folding schedule");
         let mut rates = Vec::with_capacity(num_rounds);
         let mut rate = starting_rate;
         for round in 0..num_rounds {
```

### whir/src/parameters/folding.rs
```diff
@@ -21,6 +21,16 @@ pub enum FoldingFactorError {
     /// The folding factor cannot be zero.
     #[error("Folding factor shouldn't be zero.")]
     ZeroFactor,
+
+    /// The explicit per-round folding factors fold too few variables to reach the direct-send threshold.
+    #[error(
+        "per-round folding factors leave {remaining} variables out of {num_variables}, above the direct-send threshold {threshold}; fold more variables"
+    )]
+    InsufficientFolding {
+        num_variables: usize,
+        remaining: usize,
+        threshold: usize,
+    },
 }
 
 /// Defines the folding factor for polynomial commitments.
@@ -98,14 +108,21 @@ impl FoldingFactor {
         }
     }
 
-    /// Computes the number of WHIR rounds and the number of rounds in the final sumcheck.
-    #[must_use]
-    pub fn compute_number_of_rounds(&self, num_variables: usize) -> (usize, usize) {
+    /// Compute the round schedule: number of folding rounds and final-phase variables.
+    ///
+    /// # Errors
+    ///
+    /// An explicit per-round schedule errors if a round folds more variables than remain.
+    /// It also errors if the factors together fail to reach the direct-send threshold.
+    pub fn compute_number_of_rounds(
+        &self,
+        num_variables: usize,
+    ) -> Result<(usize, usize), FoldingFactorError> {
         match self {
             Self::Constant(factor) => {
                 if num_variables <= MAX_NUM_VARIABLES_TO_SEND_COEFFS {
                     // the first folding is mandatory in the current implem (TODO don't fold, send directly the polynomial)
-                    return (0, num_variables - factor);
+                    return Ok((0, num_variables - factor));
                 }
                 // Starting from `num_variables`, each round reduces the number of variables by `factor`. As soon as the
                 // number of variables is less of equal than `MAX_NUM_VARIABLES_TO_SEND_COEFFS`, we stop folding and the
@@ -114,15 +131,15 @@ impl FoldingFactor {
                     (num_variables - MAX_NUM_VARIABLES_TO_SEND_COEFFS).div_ceil(*factor);
                 let final_sumcheck_rounds = num_variables - num_rounds * factor;
                 // The -1 accounts for the fact that the last round does not require another folding.
-                (num_rounds - 1, final_sumcheck_rounds)
+                Ok((num_rounds - 1, final_sumcheck_rounds))
             }
             Self::ConstantFromSecondRound(first_round_factor, factor) => {
                 // Compute the number of variables remaining after the first round.
                 let nv_except_first_round = num_variables - *first_round_factor;
                 if nv_except_first_round < MAX_NUM_VARIABLES_TO_SEND_COEFFS {
                     // This case is equivalent to Constant(first_round_factor)
                     // the first folding is mandatory in the current implem (TODO don't fold, send directly the polynomial)
-                    return (0, nv_except_first_round);
+                    return Ok((0, nv_except_first_round));
                 }
                 // Starting from `num_variables`, the first round reduces the number of variables by `first_round_factor`,
                 // and the next ones by `factor`. As soon as the number of variables is less of equal than
@@ -131,17 +148,32 @@ impl FoldingFactor {
                     (nv_except_first_round - MAX_NUM_VARIABLES_TO_SEND_COEFFS).div_ceil(*factor);
                 let final_sumcheck_rounds = nv_except_first_round - num_rounds * factor;
                 // No need to minus 1 because the initial round is already excepted out
-                (num_rounds, final_sumcheck_rounds)
+                Ok((num_rounds, final_sumcheck_rounds))
             }
             Self::PerRound(factors) => {
+                // Fold one explicit factor per round until the remainder reaches the threshold.
                 let mut remaining = num_variables;
                 for (i, &factor) in factors.iter().enumerate() {
+                    // A round cannot fold more variables than remain.
+                    //
+                    //     remaining = 7, factor = 9  ->  over-folds
+                    if factor > remaining {
+                        return Err(FoldingFactorError::TooLarge(factor, remaining));
+                    }
                     remaining -= factor;
+                    // Threshold reached: `i` full rounds, `remaining` sent direct.
                     if remaining <= MAX_NUM_VARIABLES_TO_SEND_COEFFS {
-                        return (i, remaining);
+                        return Ok((i, remaining));
                     }
                 }
-                panic!("Per-round folding factors do not reduce to the final coefficient threshold")
+                // Factors exhausted but the polynomial is still above the threshold.
+                //
+                //     num_variables = 20, sum(factors) = 5  ->  remaining 15 > 6
+                Err(FoldingFactorError::InsufficientFolding {
+                    num_variables,
+                    remaining,
+                    threshold: MAX_NUM_VARIABLES_TO_SEND_COEFFS,
+                })
             }
         }
     }
@@ -232,70 +264,114 @@ mod tests {
 
     #[test]
     fn test_compute_number_of_rounds() {
+        // Every valid schedule now yields `Ok((rounds, final_sumcheck_rounds))`.
         let constant_factor = 3;
         let factor = FoldingFactor::Constant(constant_factor);
         assert_eq!(
             factor.compute_number_of_rounds(MAX_NUM_VARIABLES_TO_SEND_COEFFS - 1),
-            (0, MAX_NUM_VARIABLES_TO_SEND_COEFFS - constant_factor - 1)
+            Ok((0, MAX_NUM_VARIABLES_TO_SEND_COEFFS - constant_factor - 1))
         );
         assert_eq!(
             factor.compute_number_of_rounds(MAX_NUM_VARIABLES_TO_SEND_COEFFS),
-            (0, MAX_NUM_VARIABLES_TO_SEND_COEFFS - constant_factor)
+            Ok((0, MAX_NUM_VARIABLES_TO_SEND_COEFFS - constant_factor))
         );
         assert_eq!(
             factor.compute_number_of_rounds(MAX_NUM_VARIABLES_TO_SEND_COEFFS + 1),
-            (0, MAX_NUM_VARIABLES_TO_SEND_COEFFS - constant_factor + 1)
+            Ok((0, MAX_NUM_VARIABLES_TO_SEND_COEFFS - constant_factor + 1))
         );
         assert_eq!(
             factor.compute_number_of_rounds(MAX_NUM_VARIABLES_TO_SEND_COEFFS + constant_factor),
-            (0, MAX_NUM_VARIABLES_TO_SEND_COEFFS)
+            Ok((0, MAX_NUM_VARIABLES_TO_SEND_COEFFS))
         );
         assert_eq!(
             factor.compute_number_of_rounds(MAX_NUM_VARIABLES_TO_SEND_COEFFS + constant_factor + 1),
-            (1, MAX_NUM_VARIABLES_TO_SEND_COEFFS - constant_factor + 1)
+            Ok((1, MAX_NUM_VARIABLES_TO_SEND_COEFFS - constant_factor + 1))
         );
         assert_eq!(
             factor.compute_number_of_rounds(
                 MAX_NUM_VARIABLES_TO_SEND_COEFFS + constant_factor * 2 + 1
             ),
-            (2, MAX_NUM_VARIABLES_TO_SEND_COEFFS - constant_factor + 1)
+            Ok((2, MAX_NUM_VARIABLES_TO_SEND_COEFFS - constant_factor + 1))
         );
 
         let initial_factor = 4;
         let next_factor = 3;
         let variable_factor = FoldingFactor::ConstantFromSecondRound(initial_factor, next_factor);
         assert_eq!(
             variable_factor.compute_number_of_rounds(MAX_NUM_VARIABLES_TO_SEND_COEFFS - 1),
-            (0, MAX_NUM_VARIABLES_TO_SEND_COEFFS - initial_factor - 1)
+            Ok((0, MAX_NUM_VARIABLES_TO_SEND_COEFFS - initial_factor - 1))
         );
         assert_eq!(
             variable_factor.compute_number_of_rounds(MAX_NUM_VARIABLES_TO_SEND_COEFFS),
-            (0, MAX_NUM_VARIABLES_TO_SEND_COEFFS - initial_factor)
+            Ok((0, MAX_NUM_VARIABLES_TO_SEND_COEFFS - initial_factor))
         );
         assert_eq!(
             variable_factor.compute_number_of_rounds(MAX_NUM_VARIABLES_TO_SEND_COEFFS + 1),
-            (0, MAX_NUM_VARIABLES_TO_SEND_COEFFS - initial_factor + 1)
+            Ok((0, MAX_NUM_VARIABLES_TO_SEND_COEFFS - initial_factor + 1))
         );
         assert_eq!(
             variable_factor
                 .compute_number_of_rounds(MAX_NUM_VARIABLES_TO_SEND_COEFFS + initial_factor),
-            (0, MAX_NUM_VARIABLES_TO_SEND_COEFFS)
+            Ok((0, MAX_NUM_VARIABLES_TO_SEND_COEFFS))
         );
         assert_eq!(
             variable_factor
                 .compute_number_of_rounds(MAX_NUM_VARIABLES_TO_SEND_COEFFS + initial_factor + 1),
-            (1, MAX_NUM_VARIABLES_TO_SEND_COEFFS - next_factor + 1)
+            Ok((1, MAX_NUM_VARIABLES_TO_SEND_COEFFS - next_factor + 1))
         );
         assert_eq!(
             variable_factor.compute_number_of_rounds(
                 MAX_NUM_VARIABLES_TO_SEND_COEFFS + initial_factor + next_factor + 1
             ),
-            (2, MAX_NUM_VARIABLES_TO_SEND_COEFFS - next_factor + 1)
+            Ok((2, MAX_NUM_VARIABLES_TO_SEND_COEFFS - next_factor + 1))
         );
 
+        // PerRound([3, 2]) on 10 variables: 10 -3-> 7 -2-> 5 <= 6 threshold.
         assert_eq!(
             FoldingFactor::PerRound(vec![3, 2]).compute_number_of_rounds(10),
-            (1, 5)
+            Ok((1, 5))
+        );
+    }
+
+    #[test]
+    fn per_round_factors_that_under_fold_error() {
+        // Invariant: a per-round schedule that under-folds is rejected with an error, not a panic.
+        //
+        // Fixture state:
+        //   num_variables = 20, threshold = MAX_NUM_VARIABLES_TO_SEND_COEFFS = 6
+        //   PerRound([3, 2]) folds 3 + 2 = 5 variables in total
+        //
+        //     remaining:  20 -3-> 17 -2-> 15
+        //     15 > 6  ->  schedule exhausted while still too wide
+        let schedule = FoldingFactor::PerRound(vec![3, 2]);
+
+        // The leftover variable count and threshold are reported for diagnosis.
+        assert_eq!(
+            schedule.compute_number_of_rounds(20),
+            Err(FoldingFactorError::InsufficientFolding {
+                num_variables: 20,
+                remaining: 15,
+                threshold: MAX_NUM_VARIABLES_TO_SEND_COEFFS,
+            })
+        );
+    }
+
+    #[test]
+    fn per_round_factor_larger_than_remaining_errors() {
+        // Invariant: a round cannot fold more variables than remain, even when each factor is in range.
+        //
+        // Fixture state:
+        //   num_variables = 10
+        //   PerRound([3, 9]): both factors are <= 10 individually
+        //
+        //     remaining:  10 -3-> 7 ; round 1 wants 9 > 7  ->  over-folds
+        //
+        // Without the cumulative guard this path would underflow `remaining`.
+        let schedule = FoldingFactor::PerRound(vec![3, 9]);
+
+        assert_eq!(
+            schedule.compute_number_of_rounds(10),
+            Err(FoldingFactorError::TooLarge(9, 7))
         );
     }
 
```

### whir/src/parameters/whir.rs
```diff
@@ -135,9 +135,9 @@ where
     EF: ExtensionField<F> + TwoAdicField,
     Challenger: FieldChallenger<F> + GrindingChallenger<Witness = F>,
 {
-    /// Construct an empty proof with this configuration.
+    /// Construct an empty proof shaped by this configuration.
     pub fn empty_proof<MT: Mmcs<F>>(&self) -> WhirProof<F, EF, MT> {
-        WhirProof::from_protocol_parameters(&self.params, self.num_variables)
+        WhirProof::empty(self.n_rounds(), self.final_queries)
     }
 
     /// Derive a full protocol configuration from user-facing parameters.
@@ -209,9 +209,10 @@ where
 
         // How many intermediate STIR rounds, and how many variables remain
         // for the final direct-send sumcheck.
+        // An invalid per-round schedule surfaces as a folding-factor config error.
         let (num_rounds, final_sumcheck_rounds) = whir_parameters
             .folding_factor
-            .compute_number_of_rounds(num_variables);
+            .compute_number_of_rounds(num_variables)?;
 
         let round_log_inv_rates = if whir_parameters.round_log_inv_rates.is_empty() {
             let mut rates = Vec::with_capacity(num_rounds);
@@ -616,6 +617,39 @@ mod tests {
         );
     }
 
+    #[test]
+    fn config_rejects_per_round_factors_that_under_fold() {
+        // Invariant: a per-round schedule that under-folds is rejected at config construction.
+        //
+        // Fixture state:
+        //   num_variables = 20, direct-send threshold = 6
+        //   PerRound([3, 2]) folds only 3 + 2 = 5 variables
+        //
+        //     remaining = 20 - 5 = 15 > 6  ->  under-folds
+        let mut params = default_whir_params();
+        params.folding_factor = FoldingFactor::PerRound(vec![3, 2]);
+
+        let err = WhirConfig::<F, F, MyChallenger>::new(20, params)
+            .expect_err("per-round factors under-fold; config must be rejected");
+
+        // The folding-factor error is forwarded through the config error type,
+        // carrying the variable accounting that explains the rejection.
+        match err {
+            WhirConfigError::FoldingFactor(FoldingFactorError::InsufficientFolding {
+                num_variables,
+                remaining,
+                threshold,
+            }) => {
+                assert_eq!(num_variables, 20);
+                // 20 variables minus the 3 + 2 folded by the schedule.
+                assert_eq!(remaining, 15);
+                // The direct-send threshold the schedule fails to reach.
+                assert_eq!(threshold, 6);
+            }
+            other => panic!("expected InsufficientFolding, got {other:?}"),
+        }
+    }
+
     #[test]
     fn test_n_rounds() {
         let params = default_whir_params();
```

### whir/src/pcs/proof.rs
```diff
@@ -4,7 +4,6 @@ use p3_commit::Mmcs;
 use p3_multilinear_util::poly::Poly;
 use serde::{Deserialize, Serialize};
 
-use crate::parameters::ProtocolParameters;
 pub use crate::sumcheck::SumcheckData;
 
 /// Complete WHIR proof.
@@ -131,24 +130,16 @@ pub enum QueryOpening<F, EF, Proof> {
 }
 
 impl<F: Default + Send + Sync + Clone, EF: Default, MT: Mmcs<F>> WhirProof<F, EF, MT> {
-    /// Allocate a proof structure sized for the given protocol parameters.
-    pub fn from_protocol_parameters(params: &ProtocolParameters, num_variables: usize) -> Self {
-        let (num_rounds, _final_sumcheck_rounds) = params
-            .folding_factor
-            .compute_number_of_rounds(num_variables);
-
-        let protocol_security_level = params.security_level.saturating_sub(params.pow_bits);
-
-        let num_queries = params
-            .soundness_type
-            .queries(protocol_security_level, params.starting_log_inv_rate);
-
+    /// Allocate an empty proof sized for the given intermediate-round and final-query counts.
+    pub fn empty(num_rounds: usize, num_queries: usize) -> Self {
         Self {
             initial_ood_answers: Vec::new(),
             initial_sumcheck: SumcheckData::default(),
+            // One default round-proof slot per intermediate WHIR round.
             rounds: (0..num_rounds).map(|_| WhirRoundProof::default()).collect(),
             final_poly: None,
             final_pow_witness: F::default(),
+            // Reserve space for the final-round STIR query openings.
             final_queries: Vec::with_capacity(num_queries),
             final_sumcheck: None,
         }
```

### whir/src/pcs/tests.rs
```diff
@@ -42,7 +42,9 @@ pub(crate) fn challenger() -> MyChallenger {
 }
 
 fn default_round_log_inv_rates(num_variables: usize, folding_factor: &FoldingFactor) -> Vec<usize> {
-    let (num_rounds, _) = folding_factor.compute_number_of_rounds(num_variables);
+    let (num_rounds, _) = folding_factor
+        .compute_number_of_rounds(num_variables)
+        .expect("valid folding schedule");
     let mut rates = Vec::with_capacity(num_rounds);
     let mut rate = 1;
     for round in 0..num_rounds {
```
