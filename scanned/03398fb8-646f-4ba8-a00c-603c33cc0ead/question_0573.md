# Q573: new_proof_of_space evaluates attacker-controlled generators differently across nodes

## Question
Can an unprivileged attacker reach P2P message handler `new_proof_of_space` and control generator refs, decompressed program bytes, and block-to-generator linkage so that `FarmerAPI.new_proof_of_space` in `chia/farmer/farmer_api.py` executes a path where cause `new_proof_of_space` to execute or reference generator data differently from the canonical block context, violating the invariant that all honest nodes must execute the same generator bytes and references for the same block context and leading to Consensus divergence, deterministic validation mismatch, invalid block or spend acceptance, forged weight proof trust, or chain halt caused by an unprivileged block, spend bundle, protocol message, sync path, or mempool interaction?

## Target
- File/function: chia/farmer/farmer_api.py:72 `FarmerAPI.new_proof_of_space`
- Entrypoint: P2P message handler `new_proof_of_space`
- Attacker controls: generator refs, decompressed program bytes, and block-to-generator linkage
- Exploit idea: cause `new_proof_of_space` to execute or reference generator data differently from the canonical block context
- Invariant to test: all honest nodes must execute the same generator bytes and references for the same block context
- Expected Immunefi impact: Consensus divergence, deterministic validation mismatch, invalid block or spend acceptance, forged weight proof trust, or chain halt caused by an unprivileged block, spend bundle, protocol message, sync path, or mempool interaction
- Fast validation: build paired blocks with generator-ref edge cases and assert `chia/farmer/farmer_api.py:new_proof_of_space` executes identical generator bytes on every path
