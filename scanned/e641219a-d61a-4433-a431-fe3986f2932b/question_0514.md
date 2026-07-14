# Q514: insert_root_from_merkle_blob reuses pending-root state after the security context changed

## Question
Can an unprivileged attacker reach Data Layer wallet, sync, or store flow reaching `insert_root_from_merkle_blob` and control pending roots, clear/cancel timing, and subsequent root submissions so that `DataStore.insert_root_from_merkle_blob` in `chia/data_layer/data_store.py` executes a path where make `insert_root_from_merkle_blob` reuse pending-root authority after the store's canonical security context changed, violating the invariant that pending-root state must expire when the canonical store security context no longer matches it and leading to Corruption of coin records, lineage, puzzle ownership, offer/trade settlement state, mempool or hint indexes, wallet sync state, pool membership state, or Data Layer root/store state with direct security impact?

## Target
- File/function: chia/data_layer/data_store.py:563 `DataStore.insert_root_from_merkle_blob`
- Entrypoint: Data Layer wallet, sync, or store flow reaching `insert_root_from_merkle_blob`
- Attacker controls: pending roots, clear/cancel timing, and subsequent root submissions
- Exploit idea: make `insert_root_from_merkle_blob` reuse pending-root authority after the store's canonical security context changed
- Invariant to test: pending-root state must expire when the canonical store security context no longer matches it
- Expected Immunefi impact: Corruption of coin records, lineage, puzzle ownership, offer/trade settlement state, mempool or hint indexes, wallet sync state, pool membership state, or Data Layer root/store state with direct security impact
- Fast validation: mutate canonical store context between pending-root creation and submit in `chia/data_layer/data_store.py:insert_root_from_merkle_blob` and assert stale pending roots die cleanly
