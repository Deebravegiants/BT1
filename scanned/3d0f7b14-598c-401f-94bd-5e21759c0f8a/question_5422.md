# Q5422: calldataHash integrity: find two CircomData whose getHashedCalld [when the external action is a ]

## Question
Can an unprivileged attacker find two CircomData whose getHashedCalldata1/2 keccak inputs collide via abi.encode boundary ambiguity, so the check `getHashedCalldata(circomData) == circomData.calldataHash` passes for calldata that differs from what the prover committed to, letting acted-on fields drift from the proof, specifically when the external action is a LiFi swap with attacker router calldata (where arbitrary router behaviour is injected)?

## Target
- File/function: contracts/CircomDataBuilder.sol :: getHashedCalldata / getHashedCalldata1 / getHashedCalldata2
- Entrypoint: Hinkal.transact
- Attacker controls: all CircomData fields feeding the two keccak hashes, extraData
- Exploit idea: collide or under-bind the calldata commitment
- Invariant to test: calldataHash uniquely commits to every field the contracts act on
- Expected Immunefi impact: Critical: proof or verifier bypass (unproven state accepted)
- Fast validation: Foundry: construct colliding calldata, assert both pass the integrity check
