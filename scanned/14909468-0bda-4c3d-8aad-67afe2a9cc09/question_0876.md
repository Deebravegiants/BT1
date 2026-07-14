# Q876: new_compact_vdf mixes fork state across rollback or peak changes

## Question
Can an unprivileged attacker reach full node mempool, sync, or peer flow reaching `new_compact_vdf` and control peak announcements, fork shapes, rollback order, and block delivery timing so that `FullNode.new_compact_vdf` in `chia/full_node/full_node.py` executes a path where interleave peak changes and rollback-sensitive inputs so `new_compact_vdf` mixes fork-specific state across chains, violating the invariant that fork-local state must not leak across rollback and reorg boundaries and leading to Consensus divergence, deterministic validation mismatch, invalid block or spend acceptance, forged weight proof trust, or chain halt caused by an unprivileged block, spend bundle, protocol message, sync path, or mempool interaction?

## Target
- File/function: chia/full_node/full_node.py:3265 `FullNode.new_compact_vdf`
- Entrypoint: full node mempool, sync, or peer flow reaching `new_compact_vdf`
- Attacker controls: peak announcements, fork shapes, rollback order, and block delivery timing
- Exploit idea: interleave peak changes and rollback-sensitive inputs so `new_compact_vdf` mixes fork-specific state across chains
- Invariant to test: fork-local state must not leak across rollback and reorg boundaries
- Expected Immunefi impact: Consensus divergence, deterministic validation mismatch, invalid block or spend acceptance, forged weight proof trust, or chain halt caused by an unprivileged block, spend bundle, protocol message, sync path, or mempool interaction
- Fast validation: script a reorg harness around `chia/full_node/full_node.py:new_compact_vdf` with interleaved peaks and assert fork-local state never leaks across rollback
