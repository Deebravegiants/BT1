# [?] fix(whir): return verifier errors instead of panicking on malformed proof shape (#1616)

## Summary
Severity: Unknown
Chain: ZK
Component: Plonky3/Plonky3
Published: 2026-05-11
Source: https://github.com/Plonky3/Plonky3/commit/91559f3f6d95604c453a6b32603af173f3570664
Type: security-commit

## Details
fix(whir): return verifier errors instead of panicking on malformed proof shape (#1616)

The WHIR verifier could panic on attacker-controlled malformed proofs because
several invariants were checked with `unwrap()` or direct indexing instead of
returning a `VerifierError`:

- `proof.rounds[round_index]` and `round_proof.commitment.clone().unwrap()`
  in `ParsedCommitment::parse_with_round`
- `proof.final_poly.clone()` unwrap in `WhirVerifier::verify`
- `proof.rounds[round_index].sumcheck.verify_rounds(...)` direct indexing
- `self.pow_witnesses[i]` direct indexing inside `SumcheckData::verify_rounds`

A proof with a missing round commitment, a missing final polynomial, a
`rounds` vector shorter than `n_rounds()`, or a sumcheck whose grinding
witness count diverges from its round count was enough to crash the verifier.
This is reachable from any caller that runs verification on untrusted bytes.

Changes:

- New `VerifierError` variants: `MissingRoundCommitment { round }`,
  `RoundCountMismatch { expected, actual }`, `MissingFinalPoly`.
- New `SumcheckError` variant: `PowWitnessCountMismatch { expected, actual }`.
- `ParsedCommitment::parse_with_round` now returns
  `Result<ParsedCommitment, VerifierError>`, mapping both an out-of-range
  round index and an empty commitment slot to typed errors.
- `WhirVerifier::verify` validates `proof.rounds.len() == n_rounds()` and
  the initial-sumcheck round count up front, replaces the `final_poly`
  panic site with a typed error, and propagates `parse_with_round`
  through `?`.
- `SumcheckData::verify_rounds` validates the PoW-witness count against
  the polynomial-evaluation count before the per-round loop.
- Three regression tests in `pcs/tests.rs`, each driving one shape mismatch
  through the public `MultilinearPcs::verify` API:
  * `rejects_with_round_count_mismatch_when_a_round_is_dropped`
  * `rejects_with_missing_round_commitment_when_a_root_is_cleared`
  * `rejects_with_missing_final_poly_when_cleared`

For well-formed proofs the public verification result is unchanged.

- `cargo test -p p3-whir --lib error_variant_tests` — 5 passed.
- `cargo clippy -p p3-whir --all-targets -- -D warnings` — clean.
- `cargo +nightly fmt --all -- --check` — clean.

Co-authored-by: wstran <wstran@Wilson-Tran.local>

## Patch
### whir/src/pcs/committer/reader.rs
```diff
@@ -9,6 +9,7 @@ use p3_multilinear_util::point::Point;
 use crate::constraints::statement::EqStatement;
 use crate::parameters::WhirConfig;
 use crate::pcs::proof::WhirProof;
+use crate::pcs::verifier::errors::VerifierError;
 
 /// Parsed commitment extracted from the verifier's transcript.
 ///
@@ -26,23 +27,33 @@ impl<F, D> ParsedCommitment<F, D>
 where
     F: Field,
 {
-    /// Parse a commitment for a specific round (or initial if `None`).
+    /// Parse a commitment for a specific round.
+    ///
+    /// # Errors
+    ///
+    /// - Round index is past the last round carried by the proof.
+    /// - Round entry is present but its Merkle-root slot is empty.
     pub fn parse_with_round<EF, MT: Mmcs<F>, Challenger>(
         proof: &WhirProof<F, EF, MT>,
         challenger: &mut Challenger,
         num_variables: usize,
         ood_samples: usize,
         round_index: usize,
-    ) -> ParsedCommitment<EF, MT::Commitment>
+    ) -> Result<ParsedCommitment<EF, MT::Commitment>, VerifierError>
     where
         F: TwoAdicField,
         EF: ExtensionField<F> + TwoAdicField,
         Challenger:
             FieldChallenger<F> + GrindingChallenger<Witness = F> + CanObserve<MT::Commitment>,
     {
-        // Extract root and OOD answers from either the initial commitment or a round.
-        let round_proof = &proof.rounds[round_index];
-        let root = round_proof.commitment.clone().unwrap();
+        let round_proof = proof
+            .rounds
+            .get(round_index)
+            .ok_or(VerifierError::InvalidRoundIndex { index: round_index })?;
+        let root = round_proof
+            .commitment
+            .clone()
+            .ok_or(VerifierError::MissingRoundCommitment { round: round_index })?;
         let ood_answers = round_proof.ood_answers.clone();
 
         // Observe the Merkle root in the transcript.
@@ -58,10 +69,10 @@ where
             ood_statement.add_evaluated_constraint(point, eval);
         });
 
-        ParsedCommitment {
+        Ok(ParsedCommitment {
             root,
             ood_statement,
-        }
+        })
     }
 }
 
```

### whir/src/pcs/tests.rs
```diff
@@ -372,6 +372,83 @@ mod error_variant_tests {
             other => panic!("expected OpeningBatchSizeMismatch, got {other:?}"),
         }
     }
+
+    #[test]
+    fn rejects_with_round_count_mismatch_when_a_round_is_dropped() {
+        // Invariant: round count is fixed by the protocol config.
+        //
+        // Fixture state: N honest rounds → expected = N.
+        //
+        // Mutation: drop the trailing round.
+        //
+        //     proof.whir.rounds:  [r_0, r_1, ..., r_{N-1}]  ->  [r_0, ..., r_{N-2}]
+        //     expected:           N
+        //     actual:             N - 1
+        let (pcs, commitment, mut proof, protocol) = commit_and_open();
+        assert!(
+            !proof.whir.rounds.is_empty(),
+            "fixture should produce at least one WHIR round"
+        );
+        let expected = proof.whir.rounds.len();
+        proof.whir.rounds.pop();
+
+        let err = verify(&pcs, &commitment, &proof, protocol).unwrap_err();
+        match err {
+            VerifierError::RoundCountMismatch {
+                expected: e,
+                actual: a,
+            } => {
+                assert_eq!(e, expected);
+                assert_eq!(a, expected - 1);
+            }
+            other => panic!("expected RoundCountMismatch, got {other:?}"),
+        }
+    }
+
+    #[test]
+    fn rejects_with_missing_round_commitment_when_a_root_is_cleared() {
+        // Invariant: every round must expose a Merkle root.
+        //
+        // Fixture state: round 0 carries Some(root).
+        //
+        // Mutation: clear the slot.
+        //
+        //     proof.whir.rounds[0].commitment:  Some(root)  ->  None
+        //     -> error identifies round = 0
+        let (pcs, commitment, mut proof, protocol) = commit_and_open();
+        assert!(
+            !proof.whir.rounds.is_empty(),
+            "fixture should produce at least one WHIR round"
+        );
+        proof.whir.rounds[0].commitment = None;
+
+        let err = verify(&pcs, &commitment, &proof, protocol).unwrap_err();
+        match err {
+            VerifierError::MissingRoundCommitment { round } => {
+                assert_eq!(round, 0);
+            }
+            other => panic!("expected MissingRoundCommitment, got {other:?}"),
+        }
+    }
+
+    #[test]
+    fn rejects_with_missing_final_poly_when_cleared() {
+        // Invariant: the tail polynomial is required for the final identity check.
+        //
+        // Fixture state: final_poly = Some(tail).
+        //
+        // Mutation: clear the slot.
+        //
+        //     proof.whir.final_poly:  Some(tail)  ->  None
+        let (pcs, commitment, mut proof, protocol) = commit_and_open();
+        proof.whir.final_poly = None;
+
+        let err = verify(&pcs, &commitment, &proof, protocol).unwrap_err();
+        assert!(
+            matches!(err, VerifierError::MissingFinalPoly),
+            "expected MissingFinalPoly, got {err:?}"
+        );
+    }
 }
 
 mod keccak_tests {
```

### whir/src/pcs/verifier/errors.rs
```diff
@@ -60,4 +60,16 @@ pub enum VerifierError {
     /// Proof-of-work witness verification failed.
     #[error("Invalid proof-of-work witness")]
     InvalidPowWitness,
+
+    /// Proof is missing the Merkle commitment for a round.
+    #[error("Proof is missing the Merkle commitment for round {round}")]
+    MissingRoundCommitment { round: usize },
+
+    /// Proof contains an unexpected number of rounds.
+    #[error("Proof has {actual} rounds, expected {expected}")]
+    RoundCountMismatch { expected: usize, actual: usize },
+
+    /// Proof is missing the final polynomial evaluations.
+    #[error("Proof is missing the final polynomial evaluations")]
+    MissingFinalPoly,
 }
```

### whir/src/pcs/verifier/mod.rs
```diff
@@ -21,7 +21,7 @@ use crate::constraints::statement::SelectStatement;
 use crate::parameters::{RoundConfig, WhirConfig};
 use crate::pcs::proof::{QueryOpening, WhirProof};
 use crate::sumcheck::strategy::VariableOrder;
-use crate::sumcheck::verify_final_sumcheck_rounds;
+use crate::sumcheck::{SumcheckError, verify_final_sumcheck_rounds};
 
 pub mod errors;
 
@@ -100,13 +100,32 @@ where
     where
         Challenger: CanObserve<MT::Commitment>,
     {
+        // Reject a proof that carries the wrong number of rounds before any
+        // transcript work. The per-round commitment slot is checked further
+        // down, where each round is parsed.
+        let expected_rounds = self.n_rounds();
+        if proof.rounds.len() != expected_rounds {
+            return Err(VerifierError::RoundCountMismatch {
+                expected: expected_rounds,
+                actual: proof.rounds.len(),
+            });
+        }
+
         let mut constraints = Vec::new();
         let mut round_folding_randomness = Vec::new();
         let mut prev_commitment = parsed_commitment.clone();
 
         constraints.push(initial_constraint);
 
-        // Verify the initial sumcheck.
+        // Initial sumcheck rounds == first-round folding factor.
+        let expected_initial_rounds = self.folding_factor(0);
+        let actual_initial_rounds = proof.initial_sumcheck.polynomial_evaluations().len();
+        if actual_initial_rounds != expected_initial_rounds {
+            return Err(VerifierError::Sumcheck(SumcheckError::RoundCountMismatch {
+                expected: expected_initial_rounds,
+                actual: actual_initial_rounds,
+            }));
+        }
         let folding_randomness = proof.initial_sumcheck.verify_rounds(
             challenger,
             &mut claimed_eval,
@@ -118,14 +137,15 @@ where
         for round_index in 0..self.n_rounds() {
             let round_params = &self.round_parameters[round_index];
 
-            // Parse the round commitment from the proof.
+            // Index is in bounds thanks to the length check at function entry,
+            // so only a missing commitment slot can fail here.
             let new_commitment = ParsedCommitment::<_, MT::Commitment>::parse_with_round(
                 proof,
                 challenger,
                 round_params.num_variables,
                 round_params.ood_samples,
                 round_index,
-            );
+            )?;
 
             // Verify STIR in-domain challenges against the previous commitment.
             let stir_statement = self.verify_stir_challenges(
@@ -156,9 +176,10 @@ where
         }
 
         // Final round: receive the polynomial in the clear.
-        let Some(final_evaluations) = proof.final_poly.clone() else {
-            panic!("Expected final polynomial");
-        };
+        let final_evaluations = proof
+            .final_poly
+            .clone()
+            .ok_or(VerifierError::MissingFinalPoly)?;
         challenger.observe_algebra_slice(final_evaluations.as_slice());
 
         // Verify final STIR challenges.
```

### whir/src/sumcheck/data.rs
```diff
@@ -106,6 +106,16 @@ impl<F, EF> SumcheckData<F, EF> {
     {
         let mut randomness = Vec::with_capacity(self.polynomial_evaluations.len());
 
+        // Grinding pushes one witness per round;
+        //
+        // Reject upfront if the proof is short so the loop below cannot panic on out-of-bounds indexing.
+        if pow_bits > 0 && self.pow_witnesses.len() != self.polynomial_evaluations.len() {
+            return Err(SumcheckError::PowWitnessCountMismatch {
+                expected: self.polynomial_evaluations.len(),
+                actual: self.pow_witnesses.len(),
+            });
+        }
+
         for (i, &[c0, c_inf]) in self.polynomial_evaluations.iter().enumerate() {
             // Observe only the sent polynomial evaluations (h(0) and h(inf)).
             challenger.observe_algebra_slice(&[c0, c_inf]);
```

### whir/src/sumcheck/error.rs
```diff
@@ -14,4 +14,8 @@ pub enum SumcheckError {
     /// Proof-of-work witness verification failed.
     #[error("Invalid proof-of-work witness")]
     InvalidPowWitness,
+
+    /// The proof carries fewer PoW witnesses than sumcheck rounds.
+    #[error("Sumcheck PoW witness count mismatch: expected {expected}, got {actual}")]
+    PowWitnessCountMismatch { expected: usize, actual: usize },
 }
```
