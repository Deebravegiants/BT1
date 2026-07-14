# Q1323: remove_requesting_unfinished_block derives fork choice from attacker-malleable intermediate state

## Question
Can an unprivileged attacker reach full node mempool, sync, or peer flow reaching `remove_requesting_unfinished_block` and control fork-choice inputs, intermediate peak state, and peer delivery order so that `FullNodeStore.remove_requesting_unfinished_block` in `chia/full_node/full_node_store.py` executes a path where make `remove_requesting_unfinished_block` commit fork-choice decisions from attacker-malleable intermediate state instead of canonical chain state, violating the invariant that fork choice must depend only on canonical validated chain state, not attacker-shaped transient state and leading to Consensus divergence, deterministic validation mismatch, invalid block or spend acceptance, forged weight proof trust, or chain halt caused by an unprivileged block, spend bundle, protocol message, sync path, or mempool interaction?

## Target
- File/function: chia/full_node/full_node_store.py:225 `FullNodeStore.remove_requesting_unfinished_block`
- Entrypoint: full node mempool, sync, or peer flow reaching `remove_requesting_unfinished_block`
- Attacker controls: fork-choice inputs, intermediate peak state, and peer delivery order
- Exploit idea: make `remove_requesting_unfinished_block` commit fork-choice decisions from attacker-malleable intermediate state instead of canonical chain state
- Invariant to test: fork choice must depend only on canonical validated chain state, not attacker-shaped transient state
- Expected Immunefi impact: Consensus divergence, deterministic validation mismatch, invalid block or spend acceptance, forged weight proof trust, or chain halt caused by an unprivileged block, spend bundle, protocol message, sync path, or mempool interaction
- Fast validation: deliver competing peaks and blocks around `chia/full_node/full_node_store.py:remove_requesting_unfinished_block` and assert fork choice depends only on canonical validated state
