# Q1594: validate_weight_proof_single_proc evaluates attacker-controlled generators differently across nodes

## Question
Can an unprivileged attacker reach full node mempool, sync, or peer flow reaching `validate_weight_proof_single_proc` and control generator refs, decompressed program bytes, and block-to-generator linkage so that `WeightProofHandler.validate_weight_proof_single_proc` in `chia/full_node/weight_proof.py` executes a path where cause `validate_weight_proof_single_proc` to execute or reference generator data differently from the canonical block context, violating the invariant that all honest nodes must execute the same generator bytes and references for the same block context and leading to Consensus divergence, deterministic validation mismatch, invalid block or spend acceptance, forged weight proof trust, or chain halt caused by an unprivileged block, spend bundle, protocol message, sync path, or mempool interaction?

## Target
- File/function: chia/full_node/weight_proof.py:572 `WeightProofHandler.validate_weight_proof_single_proc`
- Entrypoint: full node mempool, sync, or peer flow reaching `validate_weight_proof_single_proc`
- Attacker controls: generator refs, decompressed program bytes, and block-to-generator linkage
- Exploit idea: cause `validate_weight_proof_single_proc` to execute or reference generator data differently from the canonical block context
- Invariant to test: all honest nodes must execute the same generator bytes and references for the same block context
- Expected Immunefi impact: Consensus divergence, deterministic validation mismatch, invalid block or spend acceptance, forged weight proof trust, or chain halt caused by an unprivileged block, spend bundle, protocol message, sync path, or mempool interaction
- Fast validation: build paired blocks with generator-ref edge cases and assert `chia/full_node/weight_proof.py:validate_weight_proof_single_proc` executes identical generator bytes on every path
