# Q742: new_block_height mixes fork state across rollback or peak changes

## Question
Can an unprivileged attacker reach full node mempool, sync, or peer flow reaching `new_block_height` and control peak announcements, fork shapes, rollback order, and block delivery timing so that `FeeEstimatorInterface.new_block_height` in `chia/full_node/fee_estimator_interface.py` executes a path where interleave peak changes and rollback-sensitive inputs so `new_block_height` mixes fork-specific state across chains, violating the invariant that fork-local state must not leak across rollback and reorg boundaries and leading to Consensus divergence, deterministic validation mismatch, invalid block or spend acceptance, forged weight proof trust, or chain halt caused by an unprivileged block, spend bundle, protocol message, sync path, or mempool interaction?

## Target
- File/function: chia/full_node/fee_estimator_interface.py:12 `FeeEstimatorInterface.new_block_height`
- Entrypoint: full node mempool, sync, or peer flow reaching `new_block_height`
- Attacker controls: peak announcements, fork shapes, rollback order, and block delivery timing
- Exploit idea: interleave peak changes and rollback-sensitive inputs so `new_block_height` mixes fork-specific state across chains
- Invariant to test: fork-local state must not leak across rollback and reorg boundaries
- Expected Immunefi impact: Consensus divergence, deterministic validation mismatch, invalid block or spend acceptance, forged weight proof trust, or chain halt caused by an unprivileged block, spend bundle, protocol message, sync path, or mempool interaction
- Fast validation: script a reorg harness around `chia/full_node/fee_estimator_interface.py:new_block_height` with interleaved peaks and assert fork-local state never leaks across rollback
