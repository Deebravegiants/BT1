# Q3275: unconstrained field: slippageValues [when the token silently return]

## Question
Can an unprivileged attacker vary slippageValues between two otherwise identical transactions with the SAME valid proof, given that they gate the balance require but their sign is attacker-chosen, so the contracts act on a value the circuit never constrained at the matching public-signal index, specifically when the token silently returns false on failure (where SafeERC20 and the balance delta can disagree)?

## Target
- File/function: contracts/CircomDataBuilder.sol :: getHashedCalldata / getSignedMessageHash / formBasicInput / VerifierFacade.buildVerifierId
- Entrypoint: Hinkal.transact
- Attacker controls: slippageValues
- Exploit idea: find a field acted on downstream that is outside calldataHash, signedMessageHash and the input vector
- Invariant to test: every value the chain acts on == the value the selected circuit constrained at that index
- Expected Immunefi impact: Critical: proof or verifier bypass (unproven state accepted)
- Fast validation: Foundry: reuse one proof, mutate the field, assert both txs verify with different effects
