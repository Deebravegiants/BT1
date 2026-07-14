# Q1832: new_peak derives fork choice from attacker-malleable intermediate state

## Question
Can an unprivileged attacker reach pool wallet or singleton spend flow reaching `new_peak` and control fork-choice inputs, intermediate peak state, and peer delivery order so that `PoolWallet.new_peak` in `chia/pools/pool_wallet.py` executes a path where make `new_peak` commit fork-choice decisions from attacker-malleable intermediate state instead of canonical chain state, violating the invariant that fork choice must depend only on canonical validated chain state, not attacker-shaped transient state and leading to Consensus divergence, deterministic validation mismatch, invalid block or spend acceptance, forged weight proof trust, or chain halt caused by an unprivileged block, spend bundle, protocol message, sync path, or mempool interaction?

## Target
- File/function: chia/pools/pool_wallet.py:807 `PoolWallet.new_peak`
- Entrypoint: pool wallet or singleton spend flow reaching `new_peak`
- Attacker controls: fork-choice inputs, intermediate peak state, and peer delivery order
- Exploit idea: make `new_peak` commit fork-choice decisions from attacker-malleable intermediate state instead of canonical chain state
- Invariant to test: fork choice must depend only on canonical validated chain state, not attacker-shaped transient state
- Expected Immunefi impact: Consensus divergence, deterministic validation mismatch, invalid block or spend acceptance, forged weight proof trust, or chain halt caused by an unprivileged block, spend bundle, protocol message, sync path, or mempool interaction
- Fast validation: deliver competing peaks and blocks around `chia/pools/pool_wallet.py:new_peak` and assert fork choice depends only on canonical validated state
