# Q553: rollback_to_block derives fork choice from attacker-malleable intermediate state

## Question
Can an unprivileged attacker reach Data Layer wallet, sync, or store flow reaching `rollback_to_block` and control fork-choice inputs, intermediate peak state, and peer delivery order so that `DataLayerStore.rollback_to_block` in `chia/data_layer/dl_wallet_store.py` executes a path where make `rollback_to_block` commit fork-choice decisions from attacker-malleable intermediate state instead of canonical chain state, violating the invariant that fork choice must depend only on canonical validated chain state, not attacker-shaped transient state and leading to Consensus divergence, deterministic validation mismatch, invalid block or spend acceptance, forged weight proof trust, or chain halt caused by an unprivileged block, spend bundle, protocol message, sync path, or mempool interaction?

## Target
- File/function: chia/data_layer/dl_wallet_store.py:374 `DataLayerStore.rollback_to_block`
- Entrypoint: Data Layer wallet, sync, or store flow reaching `rollback_to_block`
- Attacker controls: fork-choice inputs, intermediate peak state, and peer delivery order
- Exploit idea: make `rollback_to_block` commit fork-choice decisions from attacker-malleable intermediate state instead of canonical chain state
- Invariant to test: fork choice must depend only on canonical validated chain state, not attacker-shaped transient state
- Expected Immunefi impact: Consensus divergence, deterministic validation mismatch, invalid block or spend acceptance, forged weight proof trust, or chain halt caused by an unprivileged block, spend bundle, protocol message, sync path, or mempool interaction
- Fast validation: deliver competing peaks and blocks around `chia/data_layer/dl_wallet_store.py:rollback_to_block` and assert fork choice depends only on canonical validated state
