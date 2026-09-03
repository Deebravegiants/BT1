# Q1396: dimensionsCheck gap: empty inputNullifiers/outCommitments mak [when the relay path is used wi]

## Question
Can an unprivileged attacker submit empty inputNullifiers/outCommitments making previousNullifierAmount 0 to skip real checks, so HinkalHelper.dimensionsCheck passes while the actual CircomData shape fed to formInputForCircom and the verifier differs from the claimed Dimensions, admitting a proof against a mismatched input vector, specifically when the relay path is used with a zero effective fee (where the relay branch changes the value split)?

## Target
- File/function: contracts/HinkalHelper.sol :: dimensionsCheck / CircomDataBuilder.formInputForCircom
- Entrypoint: Hinkal.transact
- Attacker controls: inputNullifiers, outCommitments, encryptedOutputs, dimensions, feeStructure
- Exploit idea: satisfy the length checks while the effective shape diverges
- Invariant to test: the array shapes checked == the shapes consumed to build the verifier input
- Expected Immunefi impact: Critical: proof or verifier bypass (unproven state accepted)
- Fast validation: Foundry: craft arrays passing dimensionsCheck but mismatching the vector, assert acceptance
