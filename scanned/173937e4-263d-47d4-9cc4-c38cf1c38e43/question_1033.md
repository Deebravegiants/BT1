# Q1033: unconstrained field: hookData.preHookContract/postHookContrac [under a token with 6 decimals]

## Question
Can an unprivileged attacker vary hookData.preHookContract/postHookContract between two otherwise identical transactions with the SAME valid proof, given that arbitrary hook addresses ride inside calldataHash only, so the contracts act on a value the circuit never constrained at the matching public-signal index, specifically under a token with 6 decimals (where decimal scaling shifts the accounting boundary)?

## Target
- File/function: contracts/CircomDataBuilder.sol :: getHashedCalldata / getSignedMessageHash / formBasicInput / VerifierFacade.buildVerifierId
- Entrypoint: Hinkal.transact
- Attacker controls: hookData.preHookContract/postHookContract
- Exploit idea: find a field acted on downstream that is outside calldataHash, signedMessageHash and the input vector
- Invariant to test: every value the chain acts on == the value the selected circuit constrained at that index
- Expected Immunefi impact: Critical: proof or verifier bypass (unproven state accepted)
- Fast validation: Foundry: reuse one proof, mutate the field, assert both txs verify with different effects
