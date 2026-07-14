# Q940: request_proof_of_weight evaluates attacker-controlled generators differently across nodes

## Question
Can an unprivileged attacker reach P2P message handler `request_proof_of_weight` and control generator refs, decompressed program bytes, and block-to-generator linkage so that `FullNodeAPI.request_proof_of_weight` in `chia/full_node/full_node_api.py` executes a path where cause `request_proof_of_weight` to execute or reference generator data differently from the canonical block context, violating the invariant that all honest nodes must execute the same generator bytes and references for the same block context and leading to Consensus divergence, deterministic validation mismatch, invalid block or spend acceptance, forged weight proof trust, or chain halt caused by an unprivileged block, spend bundle, protocol message, sync path, or mempool interaction?

## Target
- File/function: chia/full_node/full_node_api.py:360 `FullNodeAPI.request_proof_of_weight`
- Entrypoint: P2P message handler `request_proof_of_weight`
- Attacker controls: generator refs, decompressed program bytes, and block-to-generator linkage
- Exploit idea: cause `request_proof_of_weight` to execute or reference generator data differently from the canonical block context
- Invariant to test: all honest nodes must execute the same generator bytes and references for the same block context
- Expected Immunefi impact: Consensus divergence, deterministic validation mismatch, invalid block or spend acceptance, forged weight proof trust, or chain halt caused by an unprivileged block, spend bundle, protocol message, sync path, or mempool interaction
- Fast validation: build paired blocks with generator-ref edge cases and assert `chia/full_node/full_node_api.py:request_proof_of_weight` executes identical generator bytes on every path
