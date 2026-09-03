# Q3959: circuit constraint gap: EdDSA signature malleability accepted by [when amountChanges[i] is exact]

## Question
Can an unprivileged attacker construct witnesses using EdDSA signature malleability accepted by SignatureVerifier, where a second valid (R8,S) verifies for the same message, so a Groth16 proof validates for a spend/mint that violates the intended value or authenticity constraint of MainEVMCircuit, specifically when amountChanges[i] is exactly zero for the affected token (where the zero branch skips value movement)?

## Target
- File/function: circuits/SignatureVerifier.circom :: template constraints
- Entrypoint: Hinkal.transact (proof witness)
- Attacker controls: private circuit inputs (amounts, keys, signatures, seeds, points)
- Exploit idea: find a witness satisfying the R1CS that breaks a value/authenticity invariant
- Invariant to test: every accepted proof implies conservation and authentic ownership of the spent leaves
- Expected Immunefi impact: Critical: proof or verifier bypass (unproven state accepted)
- Fast validation: snarkjs: craft the witness, generate a proof, assert transact accepts an invalid state
