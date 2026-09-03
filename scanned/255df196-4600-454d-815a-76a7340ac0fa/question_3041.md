# Q3041: dimensionsCheck gap: feeStructure.variableRate exactly 10000  [when the token is a fee-on-tra]

## Question
Can an unprivileged attacker submit feeStructure.variableRate exactly 10000 so recipientAmount is zero and all value is fee, so HinkalHelper.dimensionsCheck passes while the actual CircomData shape fed to formInputForCircom and the verifier differs from the claimed Dimensions, admitting a proof against a mismatched input vector, specifically when the token is a fee-on-transfer token (where delivered amount is below the stated amount)?

## Target
- File/function: contracts/HinkalHelper.sol :: dimensionsCheck / CircomDataBuilder.formInputForCircom
- Entrypoint: Hinkal.transact
- Attacker controls: inputNullifiers, outCommitments, encryptedOutputs, dimensions, feeStructure
- Exploit idea: satisfy the length checks while the effective shape diverges
- Invariant to test: the array shapes checked == the shapes consumed to build the verifier input
- Expected Immunefi impact: Critical: proof or verifier bypass (unproven state accepted)
- Fast validation: Foundry: craft arrays passing dimensionsCheck but mismatching the vector, assert acceptance
