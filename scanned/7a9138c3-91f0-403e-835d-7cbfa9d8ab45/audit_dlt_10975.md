# [?] fix: WHIR verifier panics if OOB access into `proof.commitments` (#2629)

## Summary
Severity: Unknown
Chain: ZK
Component: succinctlabs/sp1
Published: 2026-03-20
Source: https://github.com/succinctlabs/sp1/commit/d11a74e3ff17993f5bb910100718c2c93169ae51
Type: security-commit

## Details
fix: WHIR verifier panics if OOB access into `proof.commitments` (#2629)

## Patch
### crates/recursion/circuit/src/basefold/whir.rs
```diff
@@ -191,6 +191,7 @@ where
 
     // For internal rounds
     pub commitments: Vec<RecursiveParsedCommitment<C, SC>>,
+    pub initial_merkle_proof: MerkleProofRounds<C, SC>,
     pub merkle_proofs: Vec<MerkleProofRounds<C, SC>>,
     pub query_proof_of_works: Vec<Felt<SP1Field>>,
     pub sumcheck_polynomials: Vec<Vec<RecursiveProverMessage>>,
@@ -338,7 +339,11 @@ impl<C: CircuitConfig, SC: SP1FieldConfigVariable<C>> RecursiveWhirVerifier<C, S
             let claim_batching_randomness: Ext<SP1Field, SP1ExtensionField> =
                 challenger.sample_ext(builder);
 
-            let merkle_proofs = &proof.merkle_proofs[round_index];
+            let merkle_proofs = if round_index != 0 {
+                &proof.merkle_proofs[round_index - 1]
+            } else {
+                &proof.initial_merkle_proof
+            };
 
             for (merkle_proof, commitment) in
                 merkle_proofs.iter().zip(prev_commitment.commitment.iter())
@@ -699,7 +704,9 @@ where
             .map(|(poly, pow)| (poly.read(builder), pow.read(builder)))
             .collect();
         let final_pow = self.final_pow.read(builder);
+        let initial_merkle_proof = self.initial_merkle_proof.read(builder);
         RecursiveWhirProof {
+            initial_merkle_proof,
             initial_sumcheck_polynomials,
             commitments,
             merkle_proofs,
@@ -740,6 +747,7 @@ where
             pow.write(witness);
         }
         self.final_pow.write(witness);
+        self.initial_merkle_proof.write(witness);
     }
 }
 
@@ -833,7 +841,8 @@ mod tests {
             .unwrap();
 
         // Verify natively.
-        let round_areas = proof.merkle_proofs[0]
+        let round_areas = proof
+            .initial_merkle_proof
             .iter()
             .map(|p| p.proof.width << config.starting_interleaved_log_height)
             .collect::<Vec<_>>();
```

### slop/crates/whir/src/prover.rs
```diff
@@ -511,8 +511,11 @@ where
             challenger,
         );
 
+        let initial_merkle_proof = merkle_proofs.remove(0);
+
         WhirProof {
             initial_sumcheck_polynomials,
+            initial_merkle_proof: initial_merkle_proof.into_iter().collect(),
             commitments: parsed_commitments,
             merkle_proofs: merkle_proofs
                 .into_iter()
```

### slop/crates/whir/src/verifier.rs
```diff
@@ -66,6 +66,7 @@ where
 {
     // First sumcheck
     pub initial_sumcheck_polynomials: Vec<(SumcheckPoly<GC::EF>, ProofOfWork<GC>)>,
+    pub initial_merkle_proof: Rounds<MerkleTreeOpeningAndProof<GC>>,
 
     // For internal rounds
     pub commitments: Vec<ParsedCommitment<GC>>,
@@ -118,6 +119,8 @@ pub enum SumcheckError {
     InvalidSum,
     #[error("invalid proof of work")]
     PowError,
+    #[error("invalid shape of proof of work")]
+    InvalidShape,
 }
 
 pub fn map_to_pow<F: AbstractField>(mut elem: F, len: usize) -> Point<F> {
@@ -174,19 +177,26 @@ where
     ) -> Result<(Point<GC::EF>, GC::EF), WhirProofError> {
         let config = &self.config;
         let n_rounds = config.round_parameters.len();
-        if commitments.len() != self.num_expected_commitments
+
+        if n_rounds == 0
+            || proof.merkle_proofs.len() != n_rounds - 1
+            || proof.query_proofs_of_work.len() != n_rounds
+            || proof.sumcheck_polynomials.len() != n_rounds
+            || proof.commitments.len() != n_rounds + 1
             || round_areas.len() != self.num_expected_commitments
-            || proof.merkle_proofs[0].len() != self.num_expected_commitments
+            || proof.initial_merkle_proof.len() != self.num_expected_commitments
         {
+            return Err(WhirProofError::IncorrectShape);
+        }
+
+        if commitments.len() != self.num_expected_commitments {
             return Err(WhirProofError::InvalidNumberOfCommitments(
                 self.num_expected_commitments,
                 commitments.len(),
             ));
         }
 
-        println!("Round areas: {round_areas:?}");
-
-        for (merkle_proof, area) in proof.merkle_proofs[0].iter().zip_eq(round_areas.iter()) {
+        for (merkle_proof, area) in proof.initial_merkle_proof.iter().zip_eq(round_areas.iter()) {
             if merkle_proof.proof.width << self.config.starting_interleaved_log_height != *area {
                 println!(
                     "proof width: {}, proof log height: {}, expected area {}, area: {}",
@@ -208,7 +218,9 @@ where
             })
             .collect();
 
-        let commitment = &proof.commitments[0];
+        // Because of the length checks at the start of the verification, the checked access isn't
+        // expected to produce an error.
+        let commitment = proof.commitments.first().ok_or(WhirProofError::IncorrectShape)?;
 
         if ood_points != commitment.ood_points {
             return Err(WhirProofError::InvalidOOD);
@@ -269,7 +281,10 @@ where
 
         for round_index in 0..n_rounds {
             let round_params = &config.round_parameters[round_index];
-            let new_commitment = &proof.commitments[round_index + 1];
+            // Because of the length checks at the start of the verification, the checked access isn't
+            // expected to produce an error.
+            let new_commitment =
+                proof.commitments.get(round_index + 1).ok_or(WhirProofError::IncorrectShape)?;
             if new_commitment.ood_answers.len() != round_params.ood_samples {
                 return Err(WhirProofError::InvalidNumberOfOODSamples(
                     round_params.ood_samples,
@@ -316,7 +331,11 @@ where
                 .collect();
             let claim_batching_randomness: GC::EF = challenger.sample_ext_element();
 
-            let merkle_proof = &proof.merkle_proofs[round_index];
+            let merkle_proof = if round_index != 0 {
+                &proof.merkle_proofs[round_index - 1]
+            } else {
+                &proof.initial_merkle_proof
+            };
 
             if round_index != 0 && merkle_proof.len() != 1 {
                 return Err(WhirProofError::IncorrectShape);
@@ -535,6 +554,9 @@ where
                 sumcheck_polynomials.len(),
             ));
         }
+        if pow_bits.len() < rounds {
+            return Err(SumcheckError::InvalidShape);
+        }
         let mut randomness = Vec::with_capacity(rounds);
         for i in 0..rounds {
             let (sumcheck_poly, pow_witness) = &sumcheck_polynomials[i];
@@ -609,7 +631,7 @@ where
     /// Functionality to deduce round by round from the proof the multiples of `1<<log.stacking_height`
     /// corresponding to the round's total polynomial size.
     fn round_multiples(proof: &<Self as MultilinearPcsVerifier<GC>>::Proof) -> Vec<usize> {
-        proof.merkle_proofs[0].iter().map(|p| p.values.sizes()[1]).collect()
+        proof.initial_merkle_proof.iter().map(|merkle_proof| merkle_proof.proof.width).collect()
     }
 }
 
```
