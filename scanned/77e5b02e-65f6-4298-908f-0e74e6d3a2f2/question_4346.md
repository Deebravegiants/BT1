# Q4346: dimensionsCheck gap: encryptedOutputs with a zero-length inne [when the feeStructure.feeToken]

## Question
Can an unprivileged attacker submit encryptedOutputs with a zero-length inner entry bypassing the >0 length require via ordering, so HinkalHelper.dimensionsCheck passes while the actual CircomData shape fed to formInputForCircom and the verifier differs from the claimed Dimensions, admitting a proof against a mismatched input vector, specifically when the feeStructure.feeToken equals the affected token (where flat/variable fee deduction overlaps the leg)?

## Target
- File/function: contracts/HinkalHelper.sol :: dimensionsCheck / CircomDataBuilder.formInputForCircom
- Entrypoint: Hinkal.transact
- Attacker controls: inputNullifiers, outCommitments, encryptedOutputs, dimensions, feeStructure
- Exploit idea: satisfy the length checks while the effective shape diverges
- Invariant to test: the array shapes checked == the shapes consumed to build the verifier input
- Expected Immunefi impact: Critical: proof or verifier bypass (unproven state accepted)
- Fast validation: Foundry: craft arrays passing dimensionsCheck but mismatching the vector, assert acceptance
