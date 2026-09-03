# Q5946: dimensionsCheck gap: onChainEncryptedOutput of length 1 to pa [when the cited root is many ba]

## Question
Can an unprivileged attacker submit onChainEncryptedOutput of length 1 to pass the >0 require while carrying no real data, so HinkalHelper.dimensionsCheck passes while the actual CircomData shape fed to formInputForCircom and the verifier differs from the claimed Dimensions, admitting a proof against a mismatched input vector, specifically when the cited root is many batches old (where a stale historical root is used for inclusion)?

## Target
- File/function: contracts/HinkalHelper.sol :: dimensionsCheck / CircomDataBuilder.formInputForCircom
- Entrypoint: Hinkal.transact
- Attacker controls: inputNullifiers, outCommitments, encryptedOutputs, dimensions, feeStructure
- Exploit idea: satisfy the length checks while the effective shape diverges
- Invariant to test: the array shapes checked == the shapes consumed to build the verifier input
- Expected Immunefi impact: Critical: proof or verifier bypass (unproven state accepted)
- Fast validation: Foundry: craft arrays passing dimensionsCheck but mismatching the vector, assert acceptance
