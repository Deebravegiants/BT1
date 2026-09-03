# Q5435: unconstrained field: dimensions.tokenNumber/nullifierAmount/o [when the external action is a ]

## Question
Can an unprivileged attacker vary dimensions.tokenNumber/nullifierAmount/outputAmount between two otherwise identical transactions with the SAME valid proof, given that they pick the verifier but are not in either hash, so the contracts act on a value the circuit never constrained at the matching public-signal index, specifically when the external action is a LiFi swap with attacker router calldata (where arbitrary router behaviour is injected)?

## Target
- File/function: contracts/CircomDataBuilder.sol :: getHashedCalldata / getSignedMessageHash / formBasicInput / VerifierFacade.buildVerifierId
- Entrypoint: Hinkal.transact
- Attacker controls: dimensions.tokenNumber/nullifierAmount/outputAmount
- Exploit idea: find a field acted on downstream that is outside calldataHash, signedMessageHash and the input vector
- Invariant to test: every value the chain acts on == the value the selected circuit constrained at that index
- Expected Immunefi impact: Critical: proof or verifier bypass (unproven state accepted)
- Fast validation: Foundry: reuse one proof, mutate the field, assert both txs verify with different effects
