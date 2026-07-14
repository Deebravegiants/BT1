# Q1437: create_block_generator2 mixes fork state across rollback or peak changes

## Question
Can an unprivileged attacker reach full node mempool, sync, or peer flow reaching `create_block_generator2` and control peak announcements, fork shapes, rollback order, and block delivery timing so that `Mempool.create_block_generator2` in `chia/full_node/mempool.py` executes a path where interleave peak changes and rollback-sensitive inputs so `create_block_generator2` mixes fork-specific state across chains, violating the invariant that fork-local state must not leak across rollback and reorg boundaries and leading to Consensus divergence, deterministic validation mismatch, invalid block or spend acceptance, forged weight proof trust, or chain halt caused by an unprivileged block, spend bundle, protocol message, sync path, or mempool interaction?

## Target
- File/function: chia/full_node/mempool.py:708 `Mempool.create_block_generator2`
- Entrypoint: full node mempool, sync, or peer flow reaching `create_block_generator2`
- Attacker controls: peak announcements, fork shapes, rollback order, and block delivery timing
- Exploit idea: interleave peak changes and rollback-sensitive inputs so `create_block_generator2` mixes fork-specific state across chains
- Invariant to test: fork-local state must not leak across rollback and reorg boundaries
- Expected Immunefi impact: Consensus divergence, deterministic validation mismatch, invalid block or spend acceptance, forged weight proof trust, or chain halt caused by an unprivileged block, spend bundle, protocol message, sync path, or mempool interaction
- Fast validation: script a reorg harness around `chia/full_node/mempool.py:create_block_generator2` with interleaved peaks and assert fork-local state never leaks across rollback
