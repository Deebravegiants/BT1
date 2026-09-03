# Q4786: verifier selection mismatch: select externalActionId so the Emporium- [when the deposit uses proofles]

## Question
Can an unprivileged attacker select externalActionId so the Emporium-min branch is taken but a normal verifier is registered, so the public-input vector built by formInputForCircom is checked against a verifier whose circuit expects a different signal layout, letting a proof validate against inputs it does not actually constrain, specifically when the deposit uses prooflessDeposit instead of a proof (where the no-proof mint path is taken)?

## Target
- File/function: contracts/VerifierFacade.sol :: buildVerifierId / verifyProof / CircomDataBuilder.formInputForCircom
- Entrypoint: Hinkal.transact
- Attacker controls: dimensions, publicSignalCount, externalActionId
- Exploit idea: decouple the verifier chosen from the circuit that produced the proof
- Invariant to test: verifier selected by buildVerifierId == the circuit that constrained this input vector
- Expected Immunefi impact: Critical: proof or verifier bypass (unproven state accepted)
- Fast validation: Hardhat: submit a proof under a mismatched Dimensions, assert verifyProof returns true wrongly
