# Q552: rollback_to_block evaluates attacker-controlled generators differently across nodes

## Question
Can an unprivileged attacker reach Data Layer wallet, sync, or store flow reaching `rollback_to_block` and control generator refs, decompressed program bytes, and block-to-generator linkage so that `DataLayerStore.rollback_to_block` in `chia/data_layer/dl_wallet_store.py` executes a path where cause `rollback_to_block` to execute or reference generator data differently from the canonical block context, violating the invariant that all honest nodes must execute the same generator bytes and references for the same block context and leading to Consensus divergence, deterministic validation mismatch, invalid block or spend acceptance, forged weight proof trust, or chain halt caused by an unprivileged block, spend bundle, protocol message, sync path, or mempool interaction?

## Target
- File/function: chia/data_layer/dl_wallet_store.py:374 `DataLayerStore.rollback_to_block`
- Entrypoint: Data Layer wallet, sync, or store flow reaching `rollback_to_block`
- Attacker controls: generator refs, decompressed program bytes, and block-to-generator linkage
- Exploit idea: cause `rollback_to_block` to execute or reference generator data differently from the canonical block context
- Invariant to test: all honest nodes must execute the same generator bytes and references for the same block context
- Expected Immunefi impact: Consensus divergence, deterministic validation mismatch, invalid block or spend acceptance, forged weight proof trust, or chain halt caused by an unprivileged block, spend bundle, protocol message, sync path, or mempool interaction
- Fast validation: build paired blocks with generator-ref edge cases and assert `chia/data_layer/dl_wallet_store.py:rollback_to_block` executes identical generator bytes on every path
