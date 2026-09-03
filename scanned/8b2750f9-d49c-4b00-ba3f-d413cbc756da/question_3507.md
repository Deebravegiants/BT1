# Q3507: Merkle/circuit root divergence when the historical root you cite is many bat [when the attacker sandwiches t]

## Question
Given that the historical root you cite is many batches old but still in the roots mapping, can an unprivileged attacker present a Groth16 proof whose MerkleRootCalculator path (with zero siblings treated as stop-here) yields a rootHashHinkal that rootHashExists accepts, for a (leaf, root) pair that Merkle.insertMany never actually produced or stored in roots, specifically when the attacker sandwiches the tx with their own deposit and withdraw (where surrounding state is attacker-tuned)?

## Target
- File/function: contracts/Merkle.sol :: insert / insertMany / insertOne / insertTwo / sortInPairs
- Entrypoint: Hinkal.transact (root check)
- Attacker controls: rootHashHinkal, rootHashHinkalIndex, the input commitment siblings/sides in the proof
- Exploit idea: exploit the difference between the on-chain frontier semantics and the circuit's truncated path
- Invariant to test: {(leaf,root) the circuit accepts} == {(leaf,root) insert* produced and stored in roots}
- Expected Immunefi impact: Critical: proof or verifier bypass (unproven state accepted)
- Fast validation: Hardhat+snarkjs: build a proof for an uninserted leaf under a stored root, assert transact succeeds
