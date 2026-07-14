# Q536: delete_singleton_records_by_launcher_id redirects or misbinds Data Layer mirror state

## Question
Can an unprivileged attacker reach Data Layer wallet, sync, or store flow reaching `delete_singleton_records_by_launcher_id` and control mirror identifiers, store ids, urls, payout-linked state, and pending-root timing so that `DataLayerStore.delete_singleton_records_by_launcher_id` in `chia/data_layer/dl_wallet_store.py` executes a path where make `delete_singleton_records_by_launcher_id` apply mirror-linked state changes to a different store, payout target, or pending-root context, violating the invariant that mirror state changes must bind to the intended store and payout-linked singleton state only and leading to Corruption of coin records, lineage, puzzle ownership, offer/trade settlement state, mempool or hint indexes, wallet sync state, pool membership state, or Data Layer root/store state with direct security impact?

## Target
- File/function: chia/data_layer/dl_wallet_store.py:250 `DataLayerStore.delete_singleton_records_by_launcher_id`
- Entrypoint: Data Layer wallet, sync, or store flow reaching `delete_singleton_records_by_launcher_id`
- Attacker controls: mirror identifiers, store ids, urls, payout-linked state, and pending-root timing
- Exploit idea: make `delete_singleton_records_by_launcher_id` apply mirror-linked state changes to a different store, payout target, or pending-root context
- Invariant to test: mirror state changes must bind to the intended store and payout-linked singleton state only
- Expected Immunefi impact: Corruption of coin records, lineage, puzzle ownership, offer/trade settlement state, mempool or hint indexes, wallet sync state, pool membership state, or Data Layer root/store state with direct security impact
- Fast validation: exercise add/delete mirror flows around pending-root changes and assert `chia/data_layer/dl_wallet_store.py:delete_singleton_records_by_launcher_id` binds every effect to the intended store
