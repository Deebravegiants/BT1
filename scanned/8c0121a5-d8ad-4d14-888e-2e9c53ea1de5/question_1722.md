# Q1722: unconstrained field: timeStamp [when the erc20TokenAddresses a]

## Question
Can an unprivileged attacker vary timeStamp between two otherwise identical transactions with the SAME valid proof, given that it stamps commitments and is reused as a swap deadline base, so the contracts act on a value the circuit never constrained at the matching public-signal index, specifically when the erc20TokenAddresses array is reordered (where index-dependent loops behave differently)?

## Target
- File/function: contracts/CircomDataBuilder.sol :: getHashedCalldata / getSignedMessageHash / formBasicInput / VerifierFacade.buildVerifierId
- Entrypoint: Hinkal.transact
- Attacker controls: timeStamp
- Exploit idea: find a field acted on downstream that is outside calldataHash, signedMessageHash and the input vector
- Invariant to test: every value the chain acts on == the value the selected circuit constrained at that index
- Expected Immunefi impact: Critical: proof or verifier bypass (unproven state accepted)
- Fast validation: Foundry: reuse one proof, mutate the field, assert both txs verify with different effects
