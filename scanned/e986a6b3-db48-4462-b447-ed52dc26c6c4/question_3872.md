# Q3872: calldataHash integrity: exploit that calldataHash is taken mod C [when amountChanges[i] is exact]

## Question
Can an unprivileged attacker exploit that calldataHash is taken mod CIRCOM_P so distinct calldata map to one field element, so the check `getHashedCalldata(circomData) == circomData.calldataHash` passes for calldata that differs from what the prover committed to, letting acted-on fields drift from the proof, specifically when amountChanges[i] is exactly zero for the affected token (where the zero branch skips value movement)?

## Target
- File/function: contracts/CircomDataBuilder.sol :: getHashedCalldata / getHashedCalldata1 / getHashedCalldata2
- Entrypoint: Hinkal.transact
- Attacker controls: all CircomData fields feeding the two keccak hashes, extraData
- Exploit idea: collide or under-bind the calldata commitment
- Invariant to test: calldataHash uniquely commits to every field the contracts act on
- Expected Immunefi impact: Critical: proof or verifier bypass (unproven state accepted)
- Fast validation: Foundry: construct colliding calldata, assert both pass the integrity check
