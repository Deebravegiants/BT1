# Q2049: new_peak_timelord derives fork choice from attacker-malleable intermediate state

## Question
Can an unprivileged attacker reach P2P message handler `new_peak_timelord` and control fork-choice inputs, intermediate peak state, and peer delivery order so that `TimelordAPI.new_peak_timelord` in `chia/timelord/timelord_api.py` executes a path where make `new_peak_timelord` commit fork-choice decisions from attacker-malleable intermediate state instead of canonical chain state, violating the invariant that fork choice must depend only on canonical validated chain state, not attacker-shaped transient state and leading to Consensus divergence, deterministic validation mismatch, invalid block or spend acceptance, forged weight proof trust, or chain halt caused by an unprivileged block, spend bundle, protocol message, sync path, or mempool interaction?

## Target
- File/function: chia/timelord/timelord_api.py:60 `TimelordAPI.new_peak_timelord`
- Entrypoint: P2P message handler `new_peak_timelord`
- Attacker controls: fork-choice inputs, intermediate peak state, and peer delivery order
- Exploit idea: make `new_peak_timelord` commit fork-choice decisions from attacker-malleable intermediate state instead of canonical chain state
- Invariant to test: fork choice must depend only on canonical validated chain state, not attacker-shaped transient state
- Expected Immunefi impact: Consensus divergence, deterministic validation mismatch, invalid block or spend acceptance, forged weight proof trust, or chain halt caused by an unprivileged block, spend bundle, protocol message, sync path, or mempool interaction
- Fast validation: deliver competing peaks and blocks around `chia/timelord/timelord_api.py:new_peak_timelord` and assert fork choice depends only on canonical validated state
