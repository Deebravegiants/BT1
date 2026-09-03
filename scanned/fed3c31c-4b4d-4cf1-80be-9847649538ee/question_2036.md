# Q2036: verifier selection mismatch: choose Dimensions whose buildVerifierId  [when the external action retur]

## Question
Can an unprivileged attacker choose Dimensions whose buildVerifierId maps to a verifier whose circuit signal order differs from formBasicInput, so the public-input vector built by formInputForCircom is checked against a verifier whose circuit expects a different signal layout, letting a proof validate against inputs it does not actually constrain, specifically when the external action returns an empty UTXO set (where utxoAmount is zero while value still moved)?

## Target
- File/function: contracts/VerifierFacade.sol :: buildVerifierId / verifyProof / CircomDataBuilder.formInputForCircom
- Entrypoint: Hinkal.transact
- Attacker controls: dimensions, publicSignalCount, externalActionId
- Exploit idea: decouple the verifier chosen from the circuit that produced the proof
- Invariant to test: verifier selected by buildVerifierId == the circuit that constrained this input vector
- Expected Immunefi impact: Critical: proof or verifier bypass (unproven state accepted)
- Fast validation: Hardhat: submit a proof under a mismatched Dimensions, assert verifyProof returns true wrongly
