# Q5710: unconstrained field: publicSignalCount [when the tree has exactly one ]

## Question
Can an unprivileged attacker vary publicSignalCount between two otherwise identical transactions with the SAME valid proof, given that it sizes the input vector but is only in calldataHash, so the contracts act on a value the circuit never constrained at the matching public-signal index, specifically when the tree has exactly one prior leaf (where roots[MINIMUM_INDEX] equals that leaf directly)?

## Target
- File/function: contracts/CircomDataBuilder.sol :: getHashedCalldata / getSignedMessageHash / formBasicInput / VerifierFacade.buildVerifierId
- Entrypoint: Hinkal.transact
- Attacker controls: publicSignalCount
- Exploit idea: find a field acted on downstream that is outside calldataHash, signedMessageHash and the input vector
- Invariant to test: every value the chain acts on == the value the selected circuit constrained at that index
- Expected Immunefi impact: Critical: proof or verifier bypass (unproven state accepted)
- Fast validation: Foundry: reuse one proof, mutate the field, assert both txs verify with different effects
