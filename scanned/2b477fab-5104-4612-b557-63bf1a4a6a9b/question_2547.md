# Q2547: calldataHash integrity: vary extraData (in calldataHash but othe [replayed across two supported ]

## Question
Can an unprivileged attacker vary extraData (in calldataHash but otherwise unused) to no effect, confirming an unbound channel, so the check `getHashedCalldata(circomData) == circomData.calldataHash` passes for calldata that differs from what the prover committed to, letting acted-on fields drift from the proof, specifically replayed across two supported chains (Base and Arbitrum) with one preimage (where cross-chain replay is in play)?

## Target
- File/function: contracts/CircomDataBuilder.sol :: getHashedCalldata / getHashedCalldata1 / getHashedCalldata2
- Entrypoint: Hinkal.transact
- Attacker controls: all CircomData fields feeding the two keccak hashes, extraData
- Exploit idea: collide or under-bind the calldata commitment
- Invariant to test: calldataHash uniquely commits to every field the contracts act on
- Expected Immunefi impact: Critical: proof or verifier bypass (unproven state accepted)
- Fast validation: Foundry: construct colliding calldata, assert both pass the integrity check
