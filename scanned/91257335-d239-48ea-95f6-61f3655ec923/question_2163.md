# Q2163: add_lineage_proof mixes fork state across rollback or peak changes

## Question
Can an unprivileged attacker reach wallet RPC or wallet sync flow reaching `add_lineage_proof` and control peak announcements, fork shapes, rollback order, and block delivery timing so that `CATLineageStore.add_lineage_proof` in `chia/wallet/cat_wallet/lineage_store.py` executes a path where interleave peak changes and rollback-sensitive inputs so `add_lineage_proof` mixes fork-specific state across chains, violating the invariant that fork-local state must not leak across rollback and reorg boundaries and leading to Consensus divergence, deterministic validation mismatch, invalid block or spend acceptance, forged weight proof trust, or chain halt caused by an unprivileged block, spend bundle, protocol message, sync path, or mempool interaction?

## Target
- File/function: chia/wallet/cat_wallet/lineage_store.py:32 `CATLineageStore.add_lineage_proof`
- Entrypoint: wallet RPC or wallet sync flow reaching `add_lineage_proof`
- Attacker controls: peak announcements, fork shapes, rollback order, and block delivery timing
- Exploit idea: interleave peak changes and rollback-sensitive inputs so `add_lineage_proof` mixes fork-specific state across chains
- Invariant to test: fork-local state must not leak across rollback and reorg boundaries
- Expected Immunefi impact: Consensus divergence, deterministic validation mismatch, invalid block or spend acceptance, forged weight proof trust, or chain halt caused by an unprivileged block, spend bundle, protocol message, sync path, or mempool interaction
- Fast validation: script a reorg harness around `chia/wallet/cat_wallet/lineage_store.py:add_lineage_proof` with interleaved peaks and assert fork-local state never leaks across rollback
