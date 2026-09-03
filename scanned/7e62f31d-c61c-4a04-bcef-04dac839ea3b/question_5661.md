# Q5661: verifier selection mismatch: set publicSignalCount so the input vecto [when the tree has exactly one ]

## Question
Can an unprivileged attacker set publicSignalCount so the input vector length matches a verifier for a different circuit shape, so the public-input vector built by formInputForCircom is checked against a verifier whose circuit expects a different signal layout, letting a proof validate against inputs it does not actually constrain, specifically when the tree has exactly one prior leaf (where roots[MINIMUM_INDEX] equals that leaf directly)?

## Target
- File/function: contracts/VerifierFacade.sol :: buildVerifierId / verifyProof / CircomDataBuilder.formInputForCircom
- Entrypoint: Hinkal.transact
- Attacker controls: dimensions, publicSignalCount, externalActionId
- Exploit idea: decouple the verifier chosen from the circuit that produced the proof
- Invariant to test: verifier selected by buildVerifierId == the circuit that constrained this input vector
- Expected Immunefi impact: Critical: proof or verifier bypass (unproven state accepted)
- Fast validation: Hardhat: submit a proof under a mismatched Dimensions, assert verifyProof returns true wrongly
