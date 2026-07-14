# Q2185: remove_lineage_proof reuses pending-root state after the security context changed

## Question
Can an unprivileged attacker reach wallet RPC or wallet sync flow reaching `remove_lineage_proof` and control pending roots, clear/cancel timing, and subsequent root submissions so that `CATLineageStore.remove_lineage_proof` in `chia/wallet/cat_wallet/lineage_store.py` executes a path where make `remove_lineage_proof` reuse pending-root authority after the store's canonical security context changed, violating the invariant that pending-root state must expire when the canonical store security context no longer matches it and leading to Corruption of coin records, lineage, puzzle ownership, offer/trade settlement state, mempool or hint indexes, wallet sync state, pool membership state, or Data Layer root/store state with direct security impact?

## Target
- File/function: chia/wallet/cat_wallet/lineage_store.py:40 `CATLineageStore.remove_lineage_proof`
- Entrypoint: wallet RPC or wallet sync flow reaching `remove_lineage_proof`
- Attacker controls: pending roots, clear/cancel timing, and subsequent root submissions
- Exploit idea: make `remove_lineage_proof` reuse pending-root authority after the store's canonical security context changed
- Invariant to test: pending-root state must expire when the canonical store security context no longer matches it
- Expected Immunefi impact: Corruption of coin records, lineage, puzzle ownership, offer/trade settlement state, mempool or hint indexes, wallet sync state, pool membership state, or Data Layer root/store state with direct security impact
- Fast validation: mutate canonical store context between pending-root creation and submit in `chia/wallet/cat_wallet/lineage_store.py:remove_lineage_proof` and assert stale pending roots die cleanly
