# Q907: new_peak mixes fork state across rollback or peak changes

## Question
Can an unprivileged attacker reach P2P message handler `new_peak` and control peak announcements, fork shapes, rollback order, and block delivery timing so that `FullNodeAPI.new_peak` in `chia/full_node/full_node_api.py` executes a path where interleave peak changes and rollback-sensitive inputs so `new_peak` mixes fork-specific state across chains, violating the invariant that fork-local state must not leak across rollback and reorg boundaries and leading to Consensus divergence, deterministic validation mismatch, invalid block or spend acceptance, forged weight proof trust, or chain halt caused by an unprivileged block, spend bundle, protocol message, sync path, or mempool interaction?

## Target
- File/function: chia/full_node/full_node_api.py:206 `FullNodeAPI.new_peak`
- Entrypoint: P2P message handler `new_peak`
- Attacker controls: peak announcements, fork shapes, rollback order, and block delivery timing
- Exploit idea: interleave peak changes and rollback-sensitive inputs so `new_peak` mixes fork-specific state across chains
- Invariant to test: fork-local state must not leak across rollback and reorg boundaries
- Expected Immunefi impact: Consensus divergence, deterministic validation mismatch, invalid block or spend acceptance, forged weight proof trust, or chain halt caused by an unprivileged block, spend bundle, protocol message, sync path, or mempool interaction
- Fast validation: script a reorg harness around `chia/full_node/full_node_api.py:new_peak` with interleaved peaks and assert fork-local state never leaks across rollback
