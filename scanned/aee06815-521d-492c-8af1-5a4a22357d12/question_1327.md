# Q1327: add_candidate_block mixes fork state across rollback or peak changes

## Question
Can an unprivileged attacker reach full node mempool, sync, or peer flow reaching `add_candidate_block` and control peak announcements, fork shapes, rollback order, and block delivery timing so that `FullNodeStore.add_candidate_block` in `chia/full_node/full_node_store.py` executes a path where interleave peak changes and rollback-sensitive inputs so `add_candidate_block` mixes fork-specific state across chains, violating the invariant that fork-local state must not leak across rollback and reorg boundaries and leading to Consensus divergence, deterministic validation mismatch, invalid block or spend acceptance, forged weight proof trust, or chain halt caused by an unprivileged block, spend bundle, protocol message, sync path, or mempool interaction?

## Target
- File/function: chia/full_node/full_node_store.py:240 `FullNodeStore.add_candidate_block`
- Entrypoint: full node mempool, sync, or peer flow reaching `add_candidate_block`
- Attacker controls: peak announcements, fork shapes, rollback order, and block delivery timing
- Exploit idea: interleave peak changes and rollback-sensitive inputs so `add_candidate_block` mixes fork-specific state across chains
- Invariant to test: fork-local state must not leak across rollback and reorg boundaries
- Expected Immunefi impact: Consensus divergence, deterministic validation mismatch, invalid block or spend acceptance, forged weight proof trust, or chain halt caused by an unprivileged block, spend bundle, protocol message, sync path, or mempool interaction
- Fast validation: script a reorg harness around `chia/full_node/full_node_store.py:add_candidate_block` with interleaved peaks and assert fork-local state never leaks across rollback
