# [?] Harden WHIR verifier against malformed proof panics (#1679)

## Summary
Severity: Unknown
Chain: ZK
Component: Plonky3/Plonky3
Published: 2026-05-19
Source: https://github.com/Plonky3/Plonky3/commit/b53b3e107ebe2f83667656fccaac6a6d656ba46c
Type: security-commit

## Details
Harden WHIR verifier against malformed proof panics (#1679)

## Patch
### whir/src/pcs/committer/reader.rs
```diff
@@ -54,7 +54,14 @@ where
             .commitment
             .clone()
             .ok_or(VerifierError::MissingRoundCommitment { round: round_index })?;
-        let ood_answers = round_proof.ood_answers.clone();
+        let ood_answers = &round_proof.ood_answers;
+        if ood_answers.len() != ood_samples {
+            return Err(VerifierError::RoundOodAnswerCountMismatch {
+                round: round_index,
+                expected: ood_samples,
+                actual: ood_answers.len(),
+            });
+        }
 
         // Observe the Merkle root in the transcript.
         challenger.observe(root.clone());
```

### whir/src/pcs/tests.rs
```diff
@@ -533,6 +533,38 @@ mod error_variant_tests {
         );
     }
 
+    #[test]
+    fn rejects_with_round_ood_answer_count_mismatch_when_answer_is_dropped() {
+        // Invariant: each round carries exactly the verifier-expected OOD answers.
+        //
+        // Fixture state: round 0 has N OOD answers.
+        //
+        // Mutation: drop one answer.
+        //
+        //     proof.whir.rounds[0].ood_answers:  N  ->  N - 1
+        let (pcs, commitment, mut proof, protocol) = commit_and_open();
+        let expected = proof.whir.rounds[0].ood_answers.len();
+        assert!(
+            expected > 0,
+            "fixture should produce at least one round-0 OOD answer"
+        );
+        proof.whir.rounds[0].ood_answers.pop();
+
+        let err = verify(&pcs, &commitment, &proof, protocol).unwrap_err();
+        match err {
+            VerifierError::RoundOodAnswerCountMismatch {
+                round,
+                expected: e,
+                actual: a,
+            } => {
+                assert_eq!(round, 0);
+                assert_eq!(e, expected);
+                assert_eq!(a, expected - 1);
+            }
+            other => panic!("expected RoundOodAnswerCountMismatch, got {other:?}"),
+        }
+    }
+
     #[test]
     fn rejects_with_stir_query_count_mismatch_when_intermediate_query_is_dropped() {
         // Invariant: queries.len() == verifier-sampled indices for the round.
```

### whir/src/pcs/verifier/errors.rs
```diff
@@ -68,6 +68,18 @@ pub enum VerifierError {
     #[error("Proof is missing the Merkle commitment for round {round}")]
     MissingRoundCommitment { round: usize },
 
+    /// Round OOD answers do not match the verifier's expected count.
+    #[error("Round {round} OOD answer count mismatch: expected {expected}, got {actual}")]
+    RoundOodAnswerCountMismatch {
+        round: usize,
+        expected: usize,
+        actual: usize,
+    },
+
+    /// Folding randomness is unexpectedly absent before a STIR check.
+    #[error("Missing folding randomness before STIR verification at round {round}")]
+    MissingFoldingRandomness { round: usize },
+
     /// Proof contains an unexpected number of rounds.
     #[error("Proof has {actual} rounds, expected {expected}")]
     RoundCountMismatch { expected: usize, actual: usize },
```

### whir/src/pcs/verifier/mod.rs
```diff
@@ -148,12 +148,15 @@ where
             )?;
 
             // Verify STIR in-domain challenges against the previous commitment.
+            let current_folding_randomness = round_folding_randomness
+                .last()
+                .ok_or(VerifierError::MissingFoldingRandomness { round: round_index })?;
             let stir_statement = self.verify_stir_challenges(
                 proof,
                 challenger,
                 round_params,
                 &prev_commitment,
-                round_folding_randomness.last().unwrap(),
+                current_folding_randomness,
                 round_index,
             )?;
 
@@ -183,12 +186,17 @@ where
         challenger.observe_algebra_slice(final_evaluations.as_slice());
 
         // Verify final STIR challenges.
+        let final_round_folding_randomness = round_folding_randomness.last().ok_or_else(|| {
+            VerifierError::MissingFoldingRandomness {
+                round: self.n_rounds(),
+            }
+        })?;
         let stir_statement = self.verify_stir_challenges(
             proof,
             challenger,
             &self.final_round_config(),
             &prev_commitment,
-            round_folding_randomness.last().unwrap(),
+            final_round_folding_randomness,
             self.n_rounds(),
         )?;
 
```
