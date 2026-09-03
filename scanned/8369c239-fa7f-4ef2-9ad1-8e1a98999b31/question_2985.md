# Q2985: unconstrained field: the a/b/c proof point encoding [when the token is a fee-on-tra]

## Question
Can an unprivileged attacker vary the a/b/c proof point encoding between two otherwise identical transactions with the SAME valid proof, given that malleable encodings can pass the same verifier, so the contracts act on a value the circuit never constrained at the matching public-signal index, specifically when the token is a fee-on-transfer token (where delivered amount is below the stated amount)?

## Target
- File/function: contracts/CircomDataBuilder.sol :: getHashedCalldata / getSignedMessageHash / formBasicInput / VerifierFacade.buildVerifierId
- Entrypoint: Hinkal.transact
- Attacker controls: the a/b/c proof point encoding
- Exploit idea: find a field acted on downstream that is outside calldataHash, signedMessageHash and the input vector
- Invariant to test: every value the chain acts on == the value the selected circuit constrained at that index
- Expected Immunefi impact: Critical: proof or verifier bypass (unproven state accepted)
- Fast validation: Foundry: reuse one proof, mutate the field, assert both txs verify with different effects
