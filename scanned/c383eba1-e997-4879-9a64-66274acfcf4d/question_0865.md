# Q865: add_compact_proof_of_time mixes fork state across rollback or peak changes

## Question
Can an unprivileged attacker reach full node mempool, sync, or peer flow reaching `add_compact_proof_of_time` and control peak announcements, fork shapes, rollback order, and block delivery timing so that `FullNode.add_compact_proof_of_time` in `chia/full_node/full_node.py` executes a path where interleave peak changes and rollback-sensitive inputs so `add_compact_proof_of_time` mixes fork-specific state across chains, violating the invariant that fork-local state must not leak across rollback and reorg boundaries and leading to Consensus divergence, deterministic validation mismatch, invalid block or spend acceptance, forged weight proof trust, or chain halt caused by an unprivileged block, spend bundle, protocol message, sync path, or mempool interaction?

## Target
- File/function: chia/full_node/full_node.py:3241 `FullNode.add_compact_proof_of_time`
- Entrypoint: full node mempool, sync, or peer flow reaching `add_compact_proof_of_time`
- Attacker controls: peak announcements, fork shapes, rollback order, and block delivery timing
- Exploit idea: interleave peak changes and rollback-sensitive inputs so `add_compact_proof_of_time` mixes fork-specific state across chains
- Invariant to test: fork-local state must not leak across rollback and reorg boundaries
- Expected Immunefi impact: Consensus divergence, deterministic validation mismatch, invalid block or spend acceptance, forged weight proof trust, or chain halt caused by an unprivileged block, spend bundle, protocol message, sync path, or mempool interaction
- Fast validation: script a reorg harness around `chia/full_node/full_node.py:add_compact_proof_of_time` with interleaved peaks and assert fork-local state never leaks across rollback
