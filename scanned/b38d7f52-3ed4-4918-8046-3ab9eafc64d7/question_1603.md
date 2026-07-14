# Q1603: validate_weight_proof mixes fork state across rollback or peak changes

## Question
Can an unprivileged attacker reach full node mempool, sync, or peer flow reaching `validate_weight_proof` and control peak announcements, fork shapes, rollback order, and block delivery timing so that `WeightProofHandler.validate_weight_proof` in `chia/full_node/weight_proof.py` executes a path where interleave peak changes and rollback-sensitive inputs so `validate_weight_proof` mixes fork-specific state across chains, violating the invariant that fork-local state must not leak across rollback and reorg boundaries and leading to Consensus divergence, deterministic validation mismatch, invalid block or spend acceptance, forged weight proof trust, or chain halt caused by an unprivileged block, spend bundle, protocol message, sync path, or mempool interaction?

## Target
- File/function: chia/full_node/weight_proof.py:605 `WeightProofHandler.validate_weight_proof`
- Entrypoint: full node mempool, sync, or peer flow reaching `validate_weight_proof`
- Attacker controls: peak announcements, fork shapes, rollback order, and block delivery timing
- Exploit idea: interleave peak changes and rollback-sensitive inputs so `validate_weight_proof` mixes fork-specific state across chains
- Invariant to test: fork-local state must not leak across rollback and reorg boundaries
- Expected Immunefi impact: Consensus divergence, deterministic validation mismatch, invalid block or spend acceptance, forged weight proof trust, or chain halt caused by an unprivileged block, spend bundle, protocol message, sync path, or mempool interaction
- Fast validation: script a reorg harness around `chia/full_node/weight_proof.py:validate_weight_proof` with interleaved peaks and assert fork-local state never leaks across rollback
