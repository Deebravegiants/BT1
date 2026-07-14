# Q900: add_to_bad_peak_cache derives fork choice from attacker-malleable intermediate state

## Question
Can an unprivileged attacker reach full node mempool, sync, or peer flow reaching `add_to_bad_peak_cache` and control fork-choice inputs, intermediate peak state, and peer delivery order so that `FullNode.add_to_bad_peak_cache` in `chia/full_node/full_node.py` executes a path where make `add_to_bad_peak_cache` commit fork-choice decisions from attacker-malleable intermediate state instead of canonical chain state, violating the invariant that fork choice must depend only on canonical validated chain state, not attacker-shaped transient state and leading to Consensus divergence, deterministic validation mismatch, invalid block or spend acceptance, forged weight proof trust, or chain halt caused by an unprivileged block, spend bundle, protocol message, sync path, or mempool interaction?

## Target
- File/function: chia/full_node/full_node.py:3357 `FullNode.add_to_bad_peak_cache`
- Entrypoint: full node mempool, sync, or peer flow reaching `add_to_bad_peak_cache`
- Attacker controls: fork-choice inputs, intermediate peak state, and peer delivery order
- Exploit idea: make `add_to_bad_peak_cache` commit fork-choice decisions from attacker-malleable intermediate state instead of canonical chain state
- Invariant to test: fork choice must depend only on canonical validated chain state, not attacker-shaped transient state
- Expected Immunefi impact: Consensus divergence, deterministic validation mismatch, invalid block or spend acceptance, forged weight proof trust, or chain halt caused by an unprivileged block, spend bundle, protocol message, sync path, or mempool interaction
- Fast validation: deliver competing peaks and blocks around `chia/full_node/full_node.py:add_to_bad_peak_cache` and assert fork choice depends only on canonical validated state
