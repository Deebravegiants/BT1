# Q825: add_block_batch derives fork choice from attacker-malleable intermediate state

## Question
Can an unprivileged attacker reach full node mempool, sync, or peer flow reaching `add_block_batch` and control fork-choice inputs, intermediate peak state, and peer delivery order so that `FullNode.add_block_batch` in `chia/full_node/full_node.py` executes a path where make `add_block_batch` commit fork-choice decisions from attacker-malleable intermediate state instead of canonical chain state, violating the invariant that fork choice must depend only on canonical validated chain state, not attacker-shaped transient state and leading to Consensus divergence, deterministic validation mismatch, invalid block or spend acceptance, forged weight proof trust, or chain halt caused by an unprivileged block, spend bundle, protocol message, sync path, or mempool interaction?

## Target
- File/function: chia/full_node/full_node.py:1544 `FullNode.add_block_batch`
- Entrypoint: full node mempool, sync, or peer flow reaching `add_block_batch`
- Attacker controls: fork-choice inputs, intermediate peak state, and peer delivery order
- Exploit idea: make `add_block_batch` commit fork-choice decisions from attacker-malleable intermediate state instead of canonical chain state
- Invariant to test: fork choice must depend only on canonical validated chain state, not attacker-shaped transient state
- Expected Immunefi impact: Consensus divergence, deterministic validation mismatch, invalid block or spend acceptance, forged weight proof trust, or chain halt caused by an unprivileged block, spend bundle, protocol message, sync path, or mempool interaction
- Fast validation: deliver competing peaks and blocks around `chia/full_node/full_node.py:add_block_batch` and assert fork choice depends only on canonical validated state
