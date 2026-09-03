# Q0335: unconstrained field: externalActionData.externalAddress [across a batch of transactions]

## Question
Can an unprivileged attacker vary externalActionData.externalAddress between two otherwise identical transactions with the SAME valid proof, given that it routes value but binding relies on the map check, so the contracts act on a value the circuit never constrained at the matching public-signal index, specifically across a batch of transactions landing in one block (where batching and ordering change the observable pre/post state)?

## Target
- File/function: contracts/CircomDataBuilder.sol :: getHashedCalldata / getSignedMessageHash / formBasicInput / VerifierFacade.buildVerifierId
- Entrypoint: Hinkal.transact
- Attacker controls: externalActionData.externalAddress
- Exploit idea: find a field acted on downstream that is outside calldataHash, signedMessageHash and the input vector
- Invariant to test: every value the chain acts on == the value the selected circuit constrained at that index
- Expected Immunefi impact: Critical: proof or verifier bypass (unproven state accepted)
- Fast validation: Foundry: reuse one proof, mutate the field, assert both txs verify with different effects
