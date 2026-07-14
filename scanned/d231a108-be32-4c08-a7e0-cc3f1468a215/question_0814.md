# Q814: send_peak_to_timelords derives fork choice from attacker-malleable intermediate state

## Question
Can an unprivileged attacker reach full node mempool, sync, or peer flow reaching `send_peak_to_timelords` and control fork-choice inputs, intermediate peak state, and peer delivery order so that `FullNode.send_peak_to_timelords` in `chia/full_node/full_node.py` executes a path where make `send_peak_to_timelords` commit fork-choice decisions from attacker-malleable intermediate state instead of canonical chain state, violating the invariant that fork choice must depend only on canonical validated chain state, not attacker-shaped transient state and leading to Consensus divergence, deterministic validation mismatch, invalid block or spend acceptance, forged weight proof trust, or chain halt caused by an unprivileged block, spend bundle, protocol message, sync path, or mempool interaction?

## Target
- File/function: chia/full_node/full_node.py:879 `FullNode.send_peak_to_timelords`
- Entrypoint: full node mempool, sync, or peer flow reaching `send_peak_to_timelords`
- Attacker controls: fork-choice inputs, intermediate peak state, and peer delivery order
- Exploit idea: make `send_peak_to_timelords` commit fork-choice decisions from attacker-malleable intermediate state instead of canonical chain state
- Invariant to test: fork choice must depend only on canonical validated chain state, not attacker-shaped transient state
- Expected Immunefi impact: Consensus divergence, deterministic validation mismatch, invalid block or spend acceptance, forged weight proof trust, or chain halt caused by an unprivileged block, spend bundle, protocol message, sync path, or mempool interaction
- Fast validation: deliver competing peaks and blocks around `chia/full_node/full_node.py:send_peak_to_timelords` and assert fork choice depends only on canonical validated state
