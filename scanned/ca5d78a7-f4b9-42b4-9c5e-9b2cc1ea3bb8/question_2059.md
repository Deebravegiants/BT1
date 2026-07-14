# Q2059: check_orphaned_unfinished_block derives fork choice from attacker-malleable intermediate state

## Question
Can an unprivileged attacker reach P2P message handler `check_orphaned_unfinished_block` and control fork-choice inputs, intermediate peak state, and peer delivery order so that `TimelordAPI.check_orphaned_unfinished_block` in `chia/timelord/timelord_api.py` executes a path where make `check_orphaned_unfinished_block` commit fork-choice decisions from attacker-malleable intermediate state instead of canonical chain state, violating the invariant that fork choice must depend only on canonical validated chain state, not attacker-shaped transient state and leading to Consensus divergence, deterministic validation mismatch, invalid block or spend acceptance, forged weight proof trust, or chain halt caused by an unprivileged block, spend bundle, protocol message, sync path, or mempool interaction?

## Target
- File/function: chia/timelord/timelord_api.py:122 `TimelordAPI.check_orphaned_unfinished_block`
- Entrypoint: P2P message handler `check_orphaned_unfinished_block`
- Attacker controls: fork-choice inputs, intermediate peak state, and peer delivery order
- Exploit idea: make `check_orphaned_unfinished_block` commit fork-choice decisions from attacker-malleable intermediate state instead of canonical chain state
- Invariant to test: fork choice must depend only on canonical validated chain state, not attacker-shaped transient state
- Expected Immunefi impact: Consensus divergence, deterministic validation mismatch, invalid block or spend acceptance, forged weight proof trust, or chain halt caused by an unprivileged block, spend bundle, protocol message, sync path, or mempool interaction
- Fast validation: deliver competing peaks and blocks around `chia/timelord/timelord_api.py:check_orphaned_unfinished_block` and assert fork choice depends only on canonical validated state
