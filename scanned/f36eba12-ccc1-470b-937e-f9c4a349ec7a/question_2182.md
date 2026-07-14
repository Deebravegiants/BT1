# Q2182: remove_lineage_proof commits or verifies a stale Data Layer root

## Question
Can an unprivileged attacker reach wallet RPC or wallet sync flow reaching `remove_lineage_proof` and control store ids, node hashes, roots, and ancestor/proof payloads so that `CATLineageStore.remove_lineage_proof` in `chia/wallet/cat_wallet/lineage_store.py` executes a path where convince `remove_lineage_proof` to accept a root, proof, or ancestor chain that belongs to the wrong logical store state, violating the invariant that each Data Layer proof, root, and ancestor chain must bind to exactly one store state and leading to Corruption of coin records, lineage, puzzle ownership, offer/trade settlement state, mempool or hint indexes, wallet sync state, pool membership state, or Data Layer root/store state with direct security impact?

## Target
- File/function: chia/wallet/cat_wallet/lineage_store.py:40 `CATLineageStore.remove_lineage_proof`
- Entrypoint: wallet RPC or wallet sync flow reaching `remove_lineage_proof`
- Attacker controls: store ids, node hashes, roots, and ancestor/proof payloads
- Exploit idea: convince `remove_lineage_proof` to accept a root, proof, or ancestor chain that belongs to the wrong logical store state
- Invariant to test: each Data Layer proof, root, and ancestor chain must bind to exactly one store state
- Expected Immunefi impact: Corruption of coin records, lineage, puzzle ownership, offer/trade settlement state, mempool or hint indexes, wallet sync state, pool membership state, or Data Layer root/store state with direct security impact
- Fast validation: feed wrong-store proofs and roots into `chia/wallet/cat_wallet/lineage_store.py:remove_lineage_proof` and assert no root or ancestor verification succeeds cross-store
