# Q0364: unconstrained field: originalSender [across a batch of transactions]

## Question
Can an unprivileged attacker vary originalSender between two otherwise identical transactions with the SAME valid proof, given that it authorises transferFrom yet is validated only in a swappable helper, so the contracts act on a value the circuit never constrained at the matching public-signal index, specifically across a batch of transactions landing in one block (where batching and ordering change the observable pre/post state)?

## Target
- File/function: contracts/CircomDataBuilder.sol :: getHashedCalldata / getSignedMessageHash / formBasicInput / VerifierFacade.buildVerifierId
- Entrypoint: Hinkal.transact
- Attacker controls: originalSender
- Exploit idea: find a field acted on downstream that is outside calldataHash, signedMessageHash and the input vector
- Invariant to test: every value the chain acts on == the value the selected circuit constrained at that index
- Expected Immunefi impact: Critical: proof or verifier bypass (unproven state accepted)
- Fast validation: Foundry: reuse one proof, mutate the field, assert both txs verify with different effects
