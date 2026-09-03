# Q0772: calldataHash integrity: mutate emporiumMessage relationship to c [when a prior tx in the same bl]

## Question
Can an unprivileged attacker mutate emporiumMessage relationship to calldataHash vs its separate public-signal use, so the check `getHashedCalldata(circomData) == circomData.calldataHash` passes for calldata that differs from what the prover committed to, letting acted-on fields drift from the proof, specifically when a prior tx in the same block left the action or tree in a partial state (where cross-tx residual state carries over)?

## Target
- File/function: contracts/CircomDataBuilder.sol :: getHashedCalldata / getHashedCalldata1 / getHashedCalldata2
- Entrypoint: Hinkal.transact
- Attacker controls: all CircomData fields feeding the two keccak hashes, extraData
- Exploit idea: collide or under-bind the calldata commitment
- Invariant to test: calldataHash uniquely commits to every field the contracts act on
- Expected Immunefi impact: Critical: proof or verifier bypass (unproven state accepted)
- Fast validation: Foundry: construct colliding calldata, assert both pass the integrity check
