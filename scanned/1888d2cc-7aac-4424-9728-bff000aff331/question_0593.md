# Q0593: unconstrained field: feeStructure.feeToken/flatFee/variableRa [when a same-token second leg i]

## Question
Can an unprivileged attacker vary feeStructure.feeToken/flatFee/variableRate between two otherwise identical transactions with the SAME valid proof, given that they steer fee math and are only in calldataHash, so the contracts act on a value the circuit never constrained at the matching public-signal index, specifically when a same-token second leg is present in the same call (where the per-token loop processes that token twice)?

## Target
- File/function: contracts/CircomDataBuilder.sol :: getHashedCalldata / getSignedMessageHash / formBasicInput / VerifierFacade.buildVerifierId
- Entrypoint: Hinkal.transact
- Attacker controls: feeStructure.feeToken/flatFee/variableRate
- Exploit idea: find a field acted on downstream that is outside calldataHash, signedMessageHash and the input vector
- Invariant to test: every value the chain acts on == the value the selected circuit constrained at that index
- Expected Immunefi impact: Critical: proof or verifier bypass (unproven state accepted)
- Fast validation: Foundry: reuse one proof, mutate the field, assert both txs verify with different effects
