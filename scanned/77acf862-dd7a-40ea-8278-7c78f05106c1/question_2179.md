# Q2179: remove_lineage_proof evaluates attacker-controlled generators differently across nodes

## Question
Can an unprivileged attacker reach wallet RPC or wallet sync flow reaching `remove_lineage_proof` and control generator refs, decompressed program bytes, and block-to-generator linkage so that `CATLineageStore.remove_lineage_proof` in `chia/wallet/cat_wallet/lineage_store.py` executes a path where cause `remove_lineage_proof` to execute or reference generator data differently from the canonical block context, violating the invariant that all honest nodes must execute the same generator bytes and references for the same block context and leading to Consensus divergence, deterministic validation mismatch, invalid block or spend acceptance, forged weight proof trust, or chain halt caused by an unprivileged block, spend bundle, protocol message, sync path, or mempool interaction?

## Target
- File/function: chia/wallet/cat_wallet/lineage_store.py:40 `CATLineageStore.remove_lineage_proof`
- Entrypoint: wallet RPC or wallet sync flow reaching `remove_lineage_proof`
- Attacker controls: generator refs, decompressed program bytes, and block-to-generator linkage
- Exploit idea: cause `remove_lineage_proof` to execute or reference generator data differently from the canonical block context
- Invariant to test: all honest nodes must execute the same generator bytes and references for the same block context
- Expected Immunefi impact: Consensus divergence, deterministic validation mismatch, invalid block or spend acceptance, forged weight proof trust, or chain halt caused by an unprivileged block, spend bundle, protocol message, sync path, or mempool interaction
- Fast validation: build paired blocks with generator-ref edge cases and assert `chia/wallet/cat_wallet/lineage_store.py:remove_lineage_proof` executes identical generator bytes on every path
