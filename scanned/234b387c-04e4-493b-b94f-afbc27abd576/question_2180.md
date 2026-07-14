# Q2180: remove_lineage_proof derives fork choice from attacker-malleable intermediate state

## Question
Can an unprivileged attacker reach wallet RPC or wallet sync flow reaching `remove_lineage_proof` and control fork-choice inputs, intermediate peak state, and peer delivery order so that `CATLineageStore.remove_lineage_proof` in `chia/wallet/cat_wallet/lineage_store.py` executes a path where make `remove_lineage_proof` commit fork-choice decisions from attacker-malleable intermediate state instead of canonical chain state, violating the invariant that fork choice must depend only on canonical validated chain state, not attacker-shaped transient state and leading to Consensus divergence, deterministic validation mismatch, invalid block or spend acceptance, forged weight proof trust, or chain halt caused by an unprivileged block, spend bundle, protocol message, sync path, or mempool interaction?

## Target
- File/function: chia/wallet/cat_wallet/lineage_store.py:40 `CATLineageStore.remove_lineage_proof`
- Entrypoint: wallet RPC or wallet sync flow reaching `remove_lineage_proof`
- Attacker controls: fork-choice inputs, intermediate peak state, and peer delivery order
- Exploit idea: make `remove_lineage_proof` commit fork-choice decisions from attacker-malleable intermediate state instead of canonical chain state
- Invariant to test: fork choice must depend only on canonical validated chain state, not attacker-shaped transient state
- Expected Immunefi impact: Consensus divergence, deterministic validation mismatch, invalid block or spend acceptance, forged weight proof trust, or chain halt caused by an unprivileged block, spend bundle, protocol message, sync path, or mempool interaction
- Fast validation: deliver competing peaks and blocks around `chia/wallet/cat_wallet/lineage_store.py:remove_lineage_proof` and assert fork choice depends only on canonical validated state
