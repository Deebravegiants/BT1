# Q587: partial_proofs evaluates attacker-controlled generators differently across nodes

## Question
Can an unprivileged attacker reach P2P message handler `partial_proofs` and control generator refs, decompressed program bytes, and block-to-generator linkage so that `FarmerAPI.partial_proofs` in `chia/farmer/farmer_api.py` executes a path where cause `partial_proofs` to execute or reference generator data differently from the canonical block context, violating the invariant that all honest nodes must execute the same generator bytes and references for the same block context and leading to Consensus divergence, deterministic validation mismatch, invalid block or spend acceptance, forged weight proof trust, or chain halt caused by an unprivileged block, spend bundle, protocol message, sync path, or mempool interaction?

## Target
- File/function: chia/farmer/farmer_api.py:495 `FarmerAPI.partial_proofs`
- Entrypoint: P2P message handler `partial_proofs`
- Attacker controls: generator refs, decompressed program bytes, and block-to-generator linkage
- Exploit idea: cause `partial_proofs` to execute or reference generator data differently from the canonical block context
- Invariant to test: all honest nodes must execute the same generator bytes and references for the same block context
- Expected Immunefi impact: Consensus divergence, deterministic validation mismatch, invalid block or spend acceptance, forged weight proof trust, or chain halt caused by an unprivileged block, spend bundle, protocol message, sync path, or mempool interaction
- Fast validation: build paired blocks with generator-ref edge cases and assert `chia/farmer/farmer_api.py:partial_proofs` executes identical generator bytes on every path
