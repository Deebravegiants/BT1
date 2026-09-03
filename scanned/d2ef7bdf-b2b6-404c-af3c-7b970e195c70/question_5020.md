# Q5020: circuit constraint gap: outAmounts encoding negatives via field  [when routed through HinkalWrap]

## Question
Can an unprivileged attacker construct witnesses using outAmounts encoding negatives via field wraparound past OverflowPreventer, where inTotal + amountChanges === outTotal holds with a wrapped negative, so a Groth16 proof validates for a spend/mint that violates the intended value or authenticity constraint of MainEVMCircuit, specifically when routed through HinkalWrapper's fee settlement first (where an extra value hop precedes Hinkal)?

## Target
- File/function: circuits/MainEVMCircuit.circom :: template constraints
- Entrypoint: Hinkal.transact (proof witness)
- Attacker controls: private circuit inputs (amounts, keys, signatures, seeds, points)
- Exploit idea: find a witness satisfying the R1CS that breaks a value/authenticity invariant
- Invariant to test: every accepted proof implies conservation and authentic ownership of the spent leaves
- Expected Immunefi impact: Critical: proof or verifier bypass (unproven state accepted)
- Fast validation: snarkjs: craft the witness, generate a proof, assert transact accepts an invalid state
