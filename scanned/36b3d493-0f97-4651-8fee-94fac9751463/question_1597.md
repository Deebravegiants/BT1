# Q1597: validate_weight_proof_single_proc commits or verifies a stale Data Layer root

## Question
Can an unprivileged attacker reach full node mempool, sync, or peer flow reaching `validate_weight_proof_single_proc` and control store ids, node hashes, roots, and ancestor/proof payloads so that `WeightProofHandler.validate_weight_proof_single_proc` in `chia/full_node/weight_proof.py` executes a path where convince `validate_weight_proof_single_proc` to accept a root, proof, or ancestor chain that belongs to the wrong logical store state, violating the invariant that each Data Layer proof, root, and ancestor chain must bind to exactly one store state and leading to Corruption of coin records, lineage, puzzle ownership, offer/trade settlement state, mempool or hint indexes, wallet sync state, pool membership state, or Data Layer root/store state with direct security impact?

## Target
- File/function: chia/full_node/weight_proof.py:572 `WeightProofHandler.validate_weight_proof_single_proc`
- Entrypoint: full node mempool, sync, or peer flow reaching `validate_weight_proof_single_proc`
- Attacker controls: store ids, node hashes, roots, and ancestor/proof payloads
- Exploit idea: convince `validate_weight_proof_single_proc` to accept a root, proof, or ancestor chain that belongs to the wrong logical store state
- Invariant to test: each Data Layer proof, root, and ancestor chain must bind to exactly one store state
- Expected Immunefi impact: Corruption of coin records, lineage, puzzle ownership, offer/trade settlement state, mempool or hint indexes, wallet sync state, pool membership state, or Data Layer root/store state with direct security impact
- Fast validation: feed wrong-store proofs and roots into `chia/full_node/weight_proof.py:validate_weight_proof_single_proc` and assert no root or ancestor verification succeeds cross-store
