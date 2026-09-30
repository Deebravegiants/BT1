# [?] fix(params): error instead of panic on infeasible WHIR/FRI params (#1737)

## Summary
Severity: Unknown
Chain: ZK
Component: Plonky3/Plonky3
Published: 2026-06-04
Source: https://github.com/Plonky3/Plonky3/commit/207173a892f88fd535681636c62686c112a5217c
Type: security-commit

## Details
fix(params): error instead of panic on infeasible WHIR/FRI params (#1737)

* fix(whir): return Result from WhirConfig::new instead of panicking

WhirConfig::new panicked on infeasible parameters: determine_ood_samples
panicked deep in a helper when no OOD count reached the security level
(reachable from the public constructor with a small field and a high
security level), and other validations used unwrap/assert.

- determine_ood_samples now returns Option (None when no count suffices).
- WhirConfig::new returns Result<Self, WhirConfigError>, converting every
  user-facing validation (folding factor, two-adicity, explicit rate and
  factor lengths, RS-domain growth, OOD feasibility) into a typed error.

Call sites in tests, benches, and the example unwrap the result.

Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>

* fix(fri): bound global max height by field two-adicity

When the verifier's input carries no commitments, the cross-check on
log_global_max_height is skipped, so a malicious proof could inflate the
fold schedule unboundedly and panic in two_adic_generator (no 2^height-th
root of unity exists past the two-adicity).

Reject it with the new FriError::GlobalMaxHeightTooLarge before the height
is used.

Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>

---------

Co-authored-by: Claude Opus 4.8 (1M context) <noreply@anthropic.com>

## Patch
### fri/src/verifier.rs
```diff
@@ -47,6 +47,13 @@ where
     InitialReducedOpeningHeightMismatch { expected: usize, got: usize },
     #[error("global max height mismatch: expected {expected}, got {got}")]
     GlobalMaxHeightMismatch { expected: usize, got: usize },
+    #[error(
+        "global max height 2^{log_global_max_height} exceeds field two-adicity 2^{two_adicity}"
+    )]
+    GlobalMaxHeightTooLarge {
+        log_global_max_height: usize,
+        two_adicity: usize,
+    },
     #[error("round {round}: sibling values length mismatch: expected {expected}, got {got}")]
     SiblingValuesLengthMismatch {
         round: usize,
@@ -222,6 +229,18 @@ where
     let total_log_reduction: usize = log_arities.iter().sum();
     let log_global_max_height = total_log_reduction + params.log_blowup + params.log_final_poly_len;
 
+    // Bound the global height by the field two-adicity before using it.
+    // The query phase evaluates the final polynomial at a 2^log_global_max_height-th
+    // root of unity, which does not exist past the two-adicity and would panic.
+    // When the input has no commitments the cross-check below is skipped, so for a
+    // malicious proof this is the only guard standing between us and that panic.
+    if log_global_max_height > Val::TWO_ADICITY {
+        return Err(FriError::GlobalMaxHeightTooLarge {
+            log_global_max_height,
+            two_adicity: Val::TWO_ADICITY,
+        });
+    }
+
     // Cross-check: the global log-height has two independent derivations which must agree.
     // Ref: Ben-Sasson et al., "Fast RS IOPP", ICALP 2018, §2.1.1.
     //
@@ -709,7 +728,7 @@ mod tests {
     use p3_commit::{BatchOpening, ExtensionMmcs, Mmcs, Pcs};
     use p3_dft::Radix2Dit;
     use p3_field::extension::BinomialExtensionField;
-    use p3_field::{Field, HornerIter, PrimeCharacteristicRing};
+    use p3_field::{Field, HornerIter, PrimeCharacteristicRing, TwoAdicField};
     use p3_matrix::dense::RowMajorMatrix;
     use p3_merkle_tree::MerkleTreeMmcs;
     use p3_symmetric::{PaddingFreeSponge, TruncatedPermutation};
@@ -1359,6 +1378,55 @@ mod tests {
         }
     }
 
+    #[test]
+    fn global_max_height_exceeds_two_adicity() {
+        // Invariant: the global height cannot exceed the field two-adicity.
+        // The final-poly point is a 2^height-th root of unity, absent past that.
+        //
+        // With no input commitments the cross-check is skipped.
+        // A malicious proof could then inflate the fold schedule without bound.
+        // The dedicated guard must reject it instead of panicking in the generator.
+        //
+        // Fixture state: 3 rounds of arity 1.
+        //
+        // Mutation: clone rounds until the schedule passes the two-adicity, then
+        // verify against an empty commitment set so only the guard stands.
+        let f = make_test_fixture();
+        let mut proof = f.proof.clone();
+
+        // Grow past the two-adicity: arity 1 per round, so rounds == sum(log_arities).
+        //     sum(log_arities) + log_blowup > TWO_ADICITY
+        let target_rounds = Val::TWO_ADICITY + 1;
+        let commit = proof.commit_phase_commits[0].clone();
+        let first_openings: Vec<_> = proof
+            .query_proofs
+            .iter()
+            .map(|qp| qp.commit_phase_openings[0].clone())
+            .collect();
+        while proof.commit_phase_commits.len() < target_rounds {
+            proof.commit_phase_commits.push(commit.clone());
+            for (qp, opening) in proof.query_proofs.iter_mut().zip(first_openings.iter()) {
+                qp.commit_phase_openings.push(opening.clone());
+            }
+        }
+
+        let mut challenger = f.challenger.clone();
+        // Empty commitments: the cross-check is skipped, leaving only the guard.
+        let err = run_verify_fri(&f.fri_params, &proof, &mut challenger, &[], &f.input_mmcs)
+            .expect_err("height above two-adicity must be rejected");
+
+        match err {
+            FriError::GlobalMaxHeightTooLarge {
+                log_global_max_height,
+                two_adicity,
+            } => {
+                assert_eq!(two_adicity, Val::TWO_ADICITY);
+                assert!(log_global_max_height > two_adicity);
+            }
+            other => panic!("wrong error variant: {other:?}"),
+        }
+    }
+
     #[test]
     fn input_proof_batch_count_mismatch() {
         let f = make_test_fixture();
```

### whir/benches/fri_vs_whir.rs
```diff
@@ -339,7 +339,7 @@ where
     };
 
     // Per-round protocol layout: query counts, OOD samples, PoW bits per round.
-    let config = WhirConfig::<EF, F, Ch>::new(num_variables, params);
+    let config = WhirConfig::<EF, F, Ch>::new(num_variables, params).unwrap();
 
     // Per-rig RNG: distinct seed per `(num_variables, log_width)` so two rigs
     // cannot accidentally collide on polynomial samples.
```

### whir/benches/whir_pcs.rs
```diff
@@ -152,7 +152,7 @@ impl<L: Layout<F, EF>> Bench<L> {
         };
 
         // Derive the per-round configuration and pre-allocate FFT twiddles.
-        let config = WhirConfig::<EF, F, Challenger>::new(opts.num_variables, params);
+        let config = WhirConfig::<EF, F, Challenger>::new(opts.num_variables, params).unwrap();
         let dft = Dft::new(1 << config.max_fft_size());
         let pcs = Pcs::<L>::new(config, dft, mmcs);
 
```

### whir/examples/whir.rs
```diff
@@ -184,7 +184,8 @@ fn main() {
     assert_eq!(witness.table_shapes(), protocol.table_shapes());
 
     // Derive the full round-by-round configuration from the committed witness.
-    let config = WhirConfig::<EF, F, MyChallenger>::new(witness.num_variables(), whir_params);
+    let config =
+        WhirConfig::<EF, F, MyChallenger>::new(witness.num_variables(), whir_params).unwrap();
     if !config.check_pow_bits() {
         warn!("more PoW bits required than what was specified");
     }
```

### whir/src/parameters/mod.rs
```diff
@@ -9,7 +9,7 @@ pub mod whir;
 
 pub use folding::{FoldingFactor, FoldingFactorError};
 pub use soundness::SecurityAssumption;
-pub use whir::{RoundConfig, WhirConfig};
+pub use whir::{RoundConfig, WhirConfig, WhirConfigError};
 
 /// Fallback proof-of-work difficulty when the user does not specify one.
 ///
```

### whir/src/parameters/soundness.rs
```diff
@@ -244,30 +244,34 @@ impl SecurityAssumption {
         (ood_samples * field_size_bits) as f64 + 1. - error
     }
 
-    /// Computes the number of OOD samples required to achieve security_level bits of security
-    /// We note that in both STIR and WHIR there are various strategies to set OOD samples.
-    /// In this case, we are just sampling one element from the extension field
+    /// Number of OOD samples needed to reach the requested security level.
+    ///
+    /// In both STIR and WHIR there are various strategies to set OOD samples.
+    /// Here we sample one element from the extension field per OOD query.
+    ///
+    /// # Returns
+    ///
+    /// - `Some(0)` for unique decoding, which uses no OOD samples.
+    /// - `Some(n)` for the smallest count reaching the security level.
+    /// - `None` when no count in range suffices, i.e. the field is too small.
     #[must_use]
     pub fn determine_ood_samples(
         &self,
         security_level: usize,
         log_degree: usize,
         log_inv_rate: usize,
         field_size_bits: usize,
-    ) -> usize {
+    ) -> Option<usize> {
         if matches!(self, Self::UniqueDecoding) {
-            return 0;
+            return Some(0);
         }
 
-        for ood_samples in 1..64 {
-            if self.ood_error(log_degree, log_inv_rate, field_size_bits, ood_samples)
+        // Each extra OOD sample adds roughly `field_size_bits - log_degree` bits.
+        // When the field is too small that term never reaches the target.
+        (1..64).find(|&ood_samples| {
+            self.ood_error(log_degree, log_inv_rate, field_size_bits, ood_samples)
                 >= security_level as f64
-            {
-                return ood_samples;
-            }
-        }
-
-        panic!("Could not find an appropriate number of OOD samples");
+        })
     }
 
     /// Compute the sumcheck soundness term of the folding step (in bits).
@@ -451,6 +455,25 @@ mod tests {
         let _ = assumption.prox_gaps_error(1, 1, 64, 0);
     }
 
+    #[test]
+    fn determine_ood_samples_reports_infeasibility() {
+        let jb = SecurityAssumption::JohnsonBound;
+
+        // A 10-bit field cannot reach 100-bit security at log-degree 20.
+        // Each OOD sample adds at most ~ (10 - 20) < 0 bits, so the loop never
+        // hits the target and the search yields nothing.
+        assert_eq!(jb.determine_ood_samples(100, 20, 2, 10), None);
+
+        // A large field reaches the target with a small sample count.
+        assert!(jb.determine_ood_samples(100, 20, 2, 128).is_some());
+
+        // Unique decoding never needs OOD samples.
+        assert_eq!(
+            SecurityAssumption::UniqueDecoding.determine_ood_samples(100, 20, 2, 10),
+            Some(0)
+        );
+    }
+
     #[test]
     fn test_ud_errors() {
         let assumption = SecurityAssumption::UniqueDecoding;
@@ -788,12 +811,15 @@ mod tests {
         let num_queries = jb.queries(security_level, log_inv_rate);
 
         // OOD sample count for the OOD term to reach security_level alone.
-        let ood_samples = jb.determine_ood_samples(
-            security_level,
-            log_degree,
-            log_inv_rate,
-            KOALABEAR_QUINTIC_BITS,
-        );
+        // The quintic field is large, so a feasible count always exists here.
+        let ood_samples = jb
+            .determine_ood_samples(
+                security_level,
+                log_degree,
+                log_inv_rate,
+                KOALABEAR_QUINTIC_BITS,
+            )
+            .expect("quintic field is large enough for these parameters");
 
         // Five algebraic error bounds at the chosen configuration.
         let prox_gap = jb.prox_gaps_error(log_degree, log_inv_rate, KOALABEAR_QUINTIC_BITS, 2);
```

### whir/src/parameters/whir.rs
```diff
@@ -7,10 +7,55 @@ use core::ops::Deref;
 use p3_challenger::{FieldChallenger, GrindingChallenger};
 use p3_commit::Mmcs;
 use p3_field::{ExtensionField, Field, TwoAdicField};
+use thiserror::Error;
 
-use super::{FoldingFactor, ProtocolParameters};
+use super::{FoldingFactor, FoldingFactorError, ProtocolParameters};
 use crate::pcs::proof::WhirProof;
 
+/// Reasons a set of user-facing parameters cannot form a valid WHIR configuration.
+#[derive(Debug, Error)]
+pub enum WhirConfigError {
+    /// The folding factor is incompatible with the polynomial size.
+    #[error(transparent)]
+    FoldingFactor(#[from] FoldingFactorError),
+
+    /// The domain after the first fold exceeds the base field two-adicity.
+    ///
+    /// - Twiddles and query equality polynomials must stay in the base field.
+    /// - A larger first-round folding factor shrinks this domain.
+    #[error(
+        "folded domain 2^{log_folded_domain_size} exceeds base-field two-adicity 2^{two_adicity}; increase the first-round folding factor"
+    )]
+    FoldedDomainExceedsTwoAdicity {
+        log_folded_domain_size: usize,
+        two_adicity: usize,
+    },
+
+    /// Explicit per-round codeword rates have the wrong length.
+    #[error("expected {expected} explicit codeword rates (one per round), got {actual}")]
+    RoundRateCountMismatch { expected: usize, actual: usize },
+
+    /// Explicit per-round folding factors have the wrong length.
+    #[error("expected {expected} explicit folding factors (one per phase), got {actual}")]
+    FoldingFactorCountMismatch { expected: usize, actual: usize },
+
+    /// A requested codeword rate would require growing the Reed-Solomon domain.
+    #[error("round {round}: requested codeword rate would require growing the RS domain")]
+    RateGrowsDomain { round: usize },
+
+    /// No out-of-domain sample count reaches the requested security level.
+    ///
+    /// - The field is too small for the requested security level.
+    /// - Lower the security level or use a larger extension field.
+    #[error(
+        "no out-of-domain sample count reaches {security_level}-bit security with a {field_size_bits}-bit field"
+    )]
+    OodSamplesInfeasible {
+        security_level: usize,
+        field_size_bits: usize,
+    },
+}
+
 /// Derived configuration for a single intermediate WHIR round.
 ///
 /// All values are computed from the user-facing protocol parameters
@@ -96,8 +141,19 @@ where
     }
 
     /// Derive a full protocol configuration from user-facing parameters.
+    ///
+    /// # Errors
+    ///
+    /// - The folding factor does not fit the polynomial size.
+    /// - The first fold leaves a domain larger than the base-field two-adicity.
+    /// - Explicit per-round rates or folding factors have the wrong length.
+    /// - A requested rate would grow the Reed-Solomon domain.
+    /// - The field is too small to reach the requested security level.
     #[allow(clippy::too_many_lines)]
-    pub fn new(num_variables: usize, whir_parameters: ProtocolParameters) -> Self {
+    pub fn new(
+        num_variables: usize,
+        whir_parameters: ProtocolParameters,
+    ) -> Result<Self, WhirConfigError> {
         // ---------------------------------------------------------------
         // Phase 1: Validate inputs and set up global constants.
         // ---------------------------------------------------------------
@@ -109,8 +165,7 @@ where
         // Reject folding factors that are incompatible with the polynomial size.
         whir_parameters
             .folding_factor
-            .check_validity(num_variables)
-            .unwrap();
+            .check_validity(num_variables)?;
 
         // PoW contributes an independent additive term to security,
         // so the algebraic protocol only needs to cover the remainder.
@@ -141,10 +196,12 @@ where
         // A larger folding_factor_0 pushes the folded domain below the limit.
         // This does NOT restrict how much data can be committed.
         let log_folded_domain_size = log_domain_size - whir_parameters.folding_factor.at_round(0);
-        assert!(
-            log_folded_domain_size <= F::TWO_ADICITY,
-            "Increase folding_factor_0"
-        );
+        if log_folded_domain_size > F::TWO_ADICITY {
+            return Err(WhirConfigError::FoldedDomainExceedsTwoAdicity {
+                log_folded_domain_size,
+                two_adicity: F::TWO_ADICITY,
+            });
+        }
 
         // ---------------------------------------------------------------
         // Phase 3: Determine round structure.
@@ -165,28 +222,36 @@ where
             }
             rates
         } else {
-            assert_eq!(
-                whir_parameters.round_log_inv_rates.len(),
-                num_rounds,
-                "Explicit codeword rates must have one entry per intermediate WHIR round"
-            );
+            if whir_parameters.round_log_inv_rates.len() != num_rounds {
+                return Err(WhirConfigError::RoundRateCountMismatch {
+                    expected: num_rounds,
+                    actual: whir_parameters.round_log_inv_rates.len(),
+                });
+            }
             whir_parameters.round_log_inv_rates.clone()
         };
-        if let FoldingFactor::PerRound(factors) = &whir_parameters.folding_factor {
-            assert_eq!(
-                factors.len(),
-                num_rounds + 1,
-                "Explicit folding factors must have one entry per folding phase"
-            );
+        if let FoldingFactor::PerRound(factors) = &whir_parameters.folding_factor
+            && factors.len() != num_rounds + 1
+        {
+            return Err(WhirConfigError::FoldingFactorCountMismatch {
+                expected: num_rounds + 1,
+                actual: factors.len(),
+            });
         }
 
         // OOD samples for the commitment phase (before any folding).
-        let commitment_ood_samples = whir_parameters.soundness_type.determine_ood_samples(
-            whir_parameters.security_level,
-            num_variables,
-            log_inv_rate,
-            field_size_bits,
-        );
+        let commitment_ood_samples = whir_parameters
+            .soundness_type
+            .determine_ood_samples(
+                whir_parameters.security_level,
+                num_variables,
+                log_inv_rate,
+                field_size_bits,
+            )
+            .ok_or(WhirConfigError::OodSamplesInfeasible {
+                security_level: whir_parameters.security_level,
+                field_size_bits,
+            })?;
 
         // PoW difficulty for the very first folding sumcheck.
         let starting_folding_pow_bits = whir_parameters.soundness_type.folding_pow_bits(
@@ -216,10 +281,9 @@ where
 
         for (round, &next_rate) in round_log_inv_rates.iter().enumerate() {
             let folding_factor = whir_parameters.folding_factor.at_round(round);
-            assert!(
-                next_rate <= log_inv_rate + folding_factor,
-                "Codeword rate would require growing the RS domain"
-            );
+            if next_rate > log_inv_rate + folding_factor {
+                return Err(WhirConfigError::RateGrowsDomain { round });
+            }
             let rs_reduction_factor = log_inv_rate + folding_factor - next_rate;
 
             // Queries use the *old* rate; OOD and folding use the *new* rate.
@@ -229,12 +293,18 @@ where
                 .queries(protocol_security_level, log_inv_rate);
 
             // OOD samples needed at the post-fold (new) rate.
-            let ood_samples = whir_parameters.soundness_type.determine_ood_samples(
-                whir_parameters.security_level,
-                num_variables,
-                next_rate,
-                field_size_bits,
-            );
+            let ood_samples = whir_parameters
+                .soundness_type
+                .determine_ood_samples(
+                    whir_parameters.security_level,
+                    num_variables,
+                    next_rate,
+                    field_size_bits,
+                )
+                .ok_or(WhirConfigError::OodSamplesInfeasible {
+                    security_level: whir_parameters.security_level,
+                    field_size_bits,
+                })?;
 
             // Two independent error sources bound the STIR round:
             //   - query_error: (1 - delta)^num_queries proximity test.
@@ -319,7 +389,7 @@ where
                 + final_sumcheck_rounds
         );
 
-        Self {
+        Ok(Self {
             params: whir_parameters,
             commitment_ood_samples,
             num_variables: initial_num_variables,
@@ -331,7 +401,7 @@ where
             final_folding_pow_bits: final_folding_pow_bits as usize,
             _extension_field: PhantomData,
             _challenger: PhantomData,
-        }
+        })
     }
 
     /// Returns the size of the initial evaluation domain.
@@ -500,17 +570,44 @@ mod tests {
     fn test_whir_config_creation() {
         let params = default_whir_params();
 
-        let config = WhirConfig::<F, F, MyChallenger>::new(10, params);
+        let config = WhirConfig::<F, F, MyChallenger>::new(10, params).unwrap();
 
         assert_eq!(config.security_level, 100);
         assert_eq!(config.params.pow_bits, 20);
         assert_eq!(config.soundness_type, SecurityAssumption::CapacityBound);
     }
 
+    #[test]
+    fn new_errors_when_field_too_small_for_security() {
+        // Invariant: an infeasible field/security pair errors instead of panicking.
+        //
+        // BabyBear used as its own extension field is 31 bits.
+        // At 31 variables the OOD term gains ~0 bits per sample.
+        // No sample count then reaches 100-bit security.
+        //
+        // Folding factor 5 keeps the folded domain at 2^27 = BabyBear two-adicity.
+        // So the two-adicity guard passes and the OOD feasibility check is reached.
+        let params = ProtocolParameters {
+            security_level: 100,
+            pow_bits: 20,
+            round_log_inv_rates: vec![],
+            folding_factor: FoldingFactor::Constant(5),
+            soundness_type: SecurityAssumption::CapacityBound,
+            starting_log_inv_rate: 1,
+        };
+
+        let err = WhirConfig::<F, F, MyChallenger>::new(31, params)
+            .expect_err("31-bit field cannot reach 100-bit security");
+        assert!(
+            matches!(err, WhirConfigError::OodSamplesInfeasible { .. }),
+            "expected OodSamplesInfeasible, got {err:?}"
+        );
+    }
+
     #[test]
     fn test_n_rounds() {
         let params = default_whir_params();
-        let config = WhirConfig::<F, F, MyChallenger>::new(10, params);
+        let config = WhirConfig::<F, F, MyChallenger>::new(10, params).unwrap();
 
         assert_eq!(config.n_rounds(), config.round_parameters.len());
     }
@@ -521,7 +618,7 @@ mod tests {
         params.folding_factor = FoldingFactor::Constant(4);
         params.round_log_inv_rates = vec![3, 2];
 
-        let config = WhirConfig::<F, F, MyChallenger>::new(16, params);
+        let config = WhirConfig::<F, F, MyChallenger>::new(16, params).unwrap();
 
         assert_eq!(config.round_parameters[0].log_inv_rate, 3);
         assert_eq!(config.round_parameters[1].log_inv_rate, 2);
@@ -534,7 +631,7 @@ mod tests {
     #[test]
     fn test_check_pow_bits_within_limits() {
         let params = default_whir_params();
-        let mut config = WhirConfig::<F, F, MyChallenger>::new(10, params);
+        let mut config = WhirConfig::<F, F, MyChallenger>::new(10, params).unwrap();
 
         // Set all values within limits
         config.params.pow_bits = 20;
@@ -577,7 +674,7 @@ mod tests {
     #[test]
     fn test_check_pow_bits_starting_folding_exceeds() {
         let params = default_whir_params();
-        let mut config = WhirConfig::<F, F, MyChallenger>::new(10, params);
+        let mut config = WhirConfig::<F, F, MyChallenger>::new(10, params).unwrap();
 
         config.params.pow_bits = 20;
         config.starting_folding_pow_bits = 21; // Exceeds max_pow_bits
@@ -593,7 +690,7 @@ mod tests {
     #[test]
     fn test_check_pow_bits_final_pow_exceeds() {
         let params = default_whir_params();
-        let mut config = WhirConfig::<F, F, MyChallenger>::new(10, params);
+        let mut config = WhirConfig::<F, F, MyChallenger>::new(10, params).unwrap();
 
         config.params.pow_bits = 20;
         config.starting_folding_pow_bits = 15;
@@ -609,7 +706,7 @@ mod tests {
     #[test]
     fn test_check_pow_bits_round_pow_exceeds() {
         let params = default_whir_params();
-        let mut config = WhirConfig::<F, F, MyChallenger>::new(10, params);
+        let mut config = WhirConfig::<F, F, MyChallenger>::new(10, params).unwrap();
 
         config.params.pow_bits = 20;
         config.starting_folding_pow_bits = 15;
@@ -638,7 +735,7 @@ mod tests {
     #[test]
     fn test_check_pow_bits_round_folding_pow_exceeds() {
         let params = default_whir_params();
-        let mut config = WhirConfig::<F, F, MyChallenger>::new(10, params);
+        let mut config = WhirConfig::<F, F, MyChallenger>::new(10, params).unwrap();
 
         config.params.pow_bits = 20;
         config.starting_folding_pow_bits = 15;
@@ -667,7 +764,7 @@ mod tests {
     #[test]
     fn test_check_pow_bits_exactly_at_limit() {
         let params = default_whir_params();
-        let mut config = WhirConfig::<F, F, MyChallenger>::new(10, params);
+        let mut config = WhirConfig::<F, F, MyChallenger>::new(10, params).unwrap();
 
         config.params.pow_bits = 20;
         config.starting_folding_pow_bits = 20;
@@ -695,7 +792,7 @@ mod tests {
     #[test]
     fn test_check_pow_bits_all_exceed() {
         let params = default_whir_params();
-        let mut config = WhirConfig::<F, F, MyChallenger>::new(10, params);
+        let mut config = WhirConfig::<F, F, MyChallenger>::new(10, params).unwrap();
 
         config.params.pow_bits = 20;
         config.starting_folding_pow_bits = 22;
```

### whir/src/pcs/tests.rs
```diff
@@ -103,7 +103,7 @@ fn run_whir_pcs_lifecycle_with_witness<L: Layout<F, EF>>(
 
     // Instantiate the PCS through the trait.
     let dft = MyDft::default();
-    let config = WhirConfig::new(num_variables, params);
+    let config = WhirConfig::new(num_variables, params).unwrap();
     let pcs = TestWhirPcs::<L>::new(config, dft, mmcs);
 
     // Prover
@@ -348,7 +348,7 @@ mod error_variant_tests {
             starting_log_inv_rate: 1,
         };
         let pcs = TestWhirPcs::<L>::new(
-            WhirConfig::new(witness.num_variables(), params),
+            WhirConfig::new(witness.num_variables(), params).unwrap(),
             MyDft::default(),
             mmcs,
         );
@@ -736,7 +736,7 @@ mod keccak_tests {
             starting_log_inv_rate: 1,
         };
         let pcs = TestWhirPcs::<L>::new(
-            WhirConfig::new(witness.num_variables(), params),
+            WhirConfig::new(witness.num_variables(), params).unwrap(),
             MyDft::default(),
             mmcs,
         );
```
