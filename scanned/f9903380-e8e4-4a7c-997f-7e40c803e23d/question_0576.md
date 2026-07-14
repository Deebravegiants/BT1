# Q576: new_proof_of_space commits or verifies a stale Data Layer root

## Question
Can an unprivileged attacker reach P2P message handler `new_proof_of_space` and control store ids, node hashes, roots, and ancestor/proof payloads so that `FarmerAPI.new_proof_of_space` in `chia/farmer/farmer_api.py` executes a path where convince `new_proof_of_space` to accept a root, proof, or ancestor chain that belongs to the wrong logical store state, violating the invariant that each Data Layer proof, root, and ancestor chain must bind to exactly one store state and leading to Corruption of coin records, lineage, puzzle ownership, offer/trade settlement state, mempool or hint indexes, wallet sync state, pool membership state, or Data Layer root/store state with direct security impact?

## Target
- File/function: chia/farmer/farmer_api.py:72 `FarmerAPI.new_proof_of_space`
- Entrypoint: P2P message handler `new_proof_of_space`
- Attacker controls: store ids, node hashes, roots, and ancestor/proof payloads
- Exploit idea: convince `new_proof_of_space` to accept a root, proof, or ancestor chain that belongs to the wrong logical store state
- Invariant to test: each Data Layer proof, root, and ancestor chain must bind to exactly one store state
- Expected Immunefi impact: Corruption of coin records, lineage, puzzle ownership, offer/trade settlement state, mempool or hint indexes, wallet sync state, pool membership state, or Data Layer root/store state with direct security impact
- Fast validation: feed wrong-store proofs and roots into `chia/farmer/farmer_api.py:new_proof_of_space` and assert no root or ancestor verification succeeds cross-store
