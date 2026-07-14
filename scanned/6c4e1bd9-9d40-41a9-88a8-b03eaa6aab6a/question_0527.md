# Q527: add_singleton_record reuses pending-root state after the security context changed

## Question
Can an unprivileged attacker reach Data Layer wallet, sync, or store flow reaching `add_singleton_record` and control pending roots, clear/cancel timing, and subsequent root submissions so that `DataLayerStore.add_singleton_record` in `chia/data_layer/dl_wallet_store.py` executes a path where make `add_singleton_record` reuse pending-root authority after the store's canonical security context changed, violating the invariant that pending-root state must expire when the canonical store security context no longer matches it and leading to Corruption of coin records, lineage, puzzle ownership, offer/trade settlement state, mempool or hint indexes, wallet sync state, pool membership state, or Data Layer root/store state with direct security impact?

## Target
- File/function: chia/data_layer/dl_wallet_store.py:111 `DataLayerStore.add_singleton_record`
- Entrypoint: Data Layer wallet, sync, or store flow reaching `add_singleton_record`
- Attacker controls: pending roots, clear/cancel timing, and subsequent root submissions
- Exploit idea: make `add_singleton_record` reuse pending-root authority after the store's canonical security context changed
- Invariant to test: pending-root state must expire when the canonical store security context no longer matches it
- Expected Immunefi impact: Corruption of coin records, lineage, puzzle ownership, offer/trade settlement state, mempool or hint indexes, wallet sync state, pool membership state, or Data Layer root/store state with direct security impact
- Fast validation: mutate canonical store context between pending-root creation and submit in `chia/data_layer/dl_wallet_store.py:add_singleton_record` and assert stale pending roots die cleanly
