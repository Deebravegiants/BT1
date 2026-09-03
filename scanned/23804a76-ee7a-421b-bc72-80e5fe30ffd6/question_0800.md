# Q0800: unconstrained field: slippageValues [when a prior tx in the same bl]

## Question
Can an unprivileged attacker vary slippageValues between two otherwise identical transactions with the SAME valid proof, given that they gate the balance require but their sign is attacker-chosen, so the contracts act on a value the circuit never constrained at the matching public-signal index, specifically when a prior tx in the same block left the action or tree in a partial state (where cross-tx residual state carries over)?

## Target
- File/function: contracts/CircomDataBuilder.sol :: getHashedCalldata / getSignedMessageHash / formBasicInput / VerifierFacade.buildVerifierId
- Entrypoint: Hinkal.transact
- Attacker controls: slippageValues
- Exploit idea: find a field acted on downstream that is outside calldataHash, signedMessageHash and the input vector
- Invariant to test: every value the chain acts on == the value the selected circuit constrained at that index
- Expected Immunefi impact: Critical: proof or verifier bypass (unproven state accepted)
- Fast validation: Foundry: reuse one proof, mutate the field, assert both txs verify with different effects
