# Q797: new_peak_sem mixes fork state across rollback or peak changes

## Question
Can an unprivileged attacker reach full node mempool, sync, or peer flow reaching `new_peak_sem` and control peak announcements, fork shapes, rollback order, and block delivery timing so that `FullNode.new_peak_sem` in `chia/full_node/full_node.py` executes a path where interleave peak changes and rollback-sensitive inputs so `new_peak_sem` mixes fork-specific state across chains, violating the invariant that fork-local state must not leak across rollback and reorg boundaries and leading to Consensus divergence, deterministic validation mismatch, invalid block or spend acceptance, forged weight proof trust, or chain halt caused by an unprivileged block, spend bundle, protocol message, sync path, or mempool interaction?

## Target
- File/function: chia/full_node/full_node.py:479 `FullNode.new_peak_sem`
- Entrypoint: full node mempool, sync, or peer flow reaching `new_peak_sem`
- Attacker controls: peak announcements, fork shapes, rollback order, and block delivery timing
- Exploit idea: interleave peak changes and rollback-sensitive inputs so `new_peak_sem` mixes fork-specific state across chains
- Invariant to test: fork-local state must not leak across rollback and reorg boundaries
- Expected Immunefi impact: Consensus divergence, deterministic validation mismatch, invalid block or spend acceptance, forged weight proof trust, or chain halt caused by an unprivileged block, spend bundle, protocol message, sync path, or mempool interaction
- Fast validation: script a reorg harness around `chia/full_node/full_node.py:new_peak_sem` with interleaved peaks and assert fork-local state never leaks across rollback
