# Q5445: circuit constraint gap: a BabyJubjub point off the prime-order s [when the external action is a ]

## Question
Can an unprivileged attacker construct witnesses using a BabyJubjub point off the prime-order subgroup slipping past BabyJubjubSubgroupCheck, where a cofactor or Ax==0 point is accepted as a valid key, so a Groth16 proof validates for a spend/mint that violates the intended value or authenticity constraint of MainEVMCircuit, specifically when the external action is a LiFi swap with attacker router calldata (where arbitrary router behaviour is injected)?

## Target
- File/function: circuits/BabyJubjubSubgroupCheck.circom :: template constraints
- Entrypoint: Hinkal.transact (proof witness)
- Attacker controls: private circuit inputs (amounts, keys, signatures, seeds, points)
- Exploit idea: find a witness satisfying the R1CS that breaks a value/authenticity invariant
- Invariant to test: every accepted proof implies conservation and authentic ownership of the spent leaves
- Expected Immunefi impact: Critical: proof or verifier bypass (unproven state accepted)
- Fast validation: snarkjs: craft the witness, generate a proof, assert transact accepts an invalid state
