# Q1167: request_compact_vdf derives fork choice from attacker-malleable intermediate state

## Question
Can an unprivileged attacker reach P2P message handler `request_compact_vdf` and control fork-choice inputs, intermediate peak state, and peer delivery order so that `FullNodeAPI.request_compact_vdf` in `chia/full_node/full_node_api.py` executes a path where make `request_compact_vdf` commit fork-choice decisions from attacker-malleable intermediate state instead of canonical chain state, violating the invariant that fork choice must depend only on canonical validated chain state, not attacker-shaped transient state and leading to Consensus divergence, deterministic validation mismatch, invalid block or spend acceptance, forged weight proof trust, or chain halt caused by an unprivileged block, spend bundle, protocol message, sync path, or mempool interaction?

## Target
- File/function: chia/full_node/full_node_api.py:1784 `FullNodeAPI.request_compact_vdf`
- Entrypoint: P2P message handler `request_compact_vdf`
- Attacker controls: fork-choice inputs, intermediate peak state, and peer delivery order
- Exploit idea: make `request_compact_vdf` commit fork-choice decisions from attacker-malleable intermediate state instead of canonical chain state
- Invariant to test: fork choice must depend only on canonical validated chain state, not attacker-shaped transient state
- Expected Immunefi impact: Consensus divergence, deterministic validation mismatch, invalid block or spend acceptance, forged weight proof trust, or chain halt caused by an unprivileged block, spend bundle, protocol message, sync path, or mempool interaction
- Fast validation: deliver competing peaks and blocks around `chia/full_node/full_node_api.py:request_compact_vdf` and assert fork choice depends only on canonical validated state
