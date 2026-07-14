# Q206: create_store reuses pending-root state after the security context changed

## Question
Can an unprivileged attacker reach Data Layer wallet, sync, or store flow reaching `create_store` and control pending roots, clear/cancel timing, and subsequent root submissions so that `DataLayer.create_store` in `chia/data_layer/data_layer.py` executes a path where make `create_store` reuse pending-root authority after the store's canonical security context changed, violating the invariant that pending-root state must expire when the canonical store security context no longer matches it and leading to Corruption of coin records, lineage, puzzle ownership, offer/trade settlement state, mempool or hint indexes, wallet sync state, pool membership state, or Data Layer root/store state with direct security impact?

## Target
- File/function: chia/data_layer/data_layer.py:294 `DataLayer.create_store`
- Entrypoint: Data Layer wallet, sync, or store flow reaching `create_store`
- Attacker controls: pending roots, clear/cancel timing, and subsequent root submissions
- Exploit idea: make `create_store` reuse pending-root authority after the store's canonical security context changed
- Invariant to test: pending-root state must expire when the canonical store security context no longer matches it
- Expected Immunefi impact: Corruption of coin records, lineage, puzzle ownership, offer/trade settlement state, mempool or hint indexes, wallet sync state, pool membership state, or Data Layer root/store state with direct security impact
- Fast validation: mutate canonical store context between pending-root creation and submit in `chia/data_layer/data_layer.py:create_store` and assert stale pending roots die cleanly
