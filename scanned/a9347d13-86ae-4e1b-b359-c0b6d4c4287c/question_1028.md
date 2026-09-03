# Q1028: circuit constraint gap: messageSeed reuse so message == Poseidon [under a token with 6 decimals]

## Question
Can an unprivileged attacker construct witnesses using messageSeed reuse so message == Poseidon(messageSeed) collides across Emporium calls, where the pinned message is not bound to the spend, so a Groth16 proof validates for a spend/mint that violates the intended value or authenticity constraint of MainEVMCircuit, specifically under a token with 6 decimals (where decimal scaling shifts the accounting boundary)?

## Target
- File/function: circuits/MainEVMCircuit.circom :: template constraints
- Entrypoint: Hinkal.transact (proof witness)
- Attacker controls: private circuit inputs (amounts, keys, signatures, seeds, points)
- Exploit idea: find a witness satisfying the R1CS that breaks a value/authenticity invariant
- Invariant to test: every accepted proof implies conservation and authentic ownership of the spent leaves
- Expected Immunefi impact: Critical: proof or verifier bypass (unproven state accepted)
- Fast validation: snarkjs: craft the witness, generate a proof, assert transact accepts an invalid state
