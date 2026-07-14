# Q551: rollback_to_block reuses cached validation state for non-equivalent blocks

## Question
Can an unprivileged attacker reach Data Layer wallet, sync, or store flow reaching `rollback_to_block` and control non-equivalent blocks or proofs that collide in cache or dedup assumptions so that `DataLayerStore.rollback_to_block` in `chia/data_layer/dl_wallet_store.py` executes a path where reuse cache, dedup, or seen-set assumptions in `rollback_to_block` for attacker-supplied objects that are not actually equivalent, violating the invariant that cache hits must never substitute for validating non-equivalent attacker-controlled data and leading to Consensus divergence, deterministic validation mismatch, invalid block or spend acceptance, forged weight proof trust, or chain halt caused by an unprivileged block, spend bundle, protocol message, sync path, or mempool interaction?

## Target
- File/function: chia/data_layer/dl_wallet_store.py:374 `DataLayerStore.rollback_to_block`
- Entrypoint: Data Layer wallet, sync, or store flow reaching `rollback_to_block`
- Attacker controls: non-equivalent blocks or proofs that collide in cache or dedup assumptions
- Exploit idea: reuse cache, dedup, or seen-set assumptions in `rollback_to_block` for attacker-supplied objects that are not actually equivalent
- Invariant to test: cache hits must never substitute for validating non-equivalent attacker-controlled data
- Expected Immunefi impact: Consensus divergence, deterministic validation mismatch, invalid block or spend acceptance, forged weight proof trust, or chain halt caused by an unprivileged block, spend bundle, protocol message, sync path, or mempool interaction
- Fast validation: hit `chia/data_layer/dl_wallet_store.py:rollback_to_block` with non-equivalent objects that share cache-sensitive identifiers and assert no validation reuse changes outcome
