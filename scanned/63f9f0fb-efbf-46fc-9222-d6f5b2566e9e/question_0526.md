# Q526: add_singleton_record redirects or misbinds Data Layer mirror state

## Question
Can an unprivileged attacker reach Data Layer wallet, sync, or store flow reaching `add_singleton_record` and control mirror identifiers, store ids, urls, payout-linked state, and pending-root timing so that `DataLayerStore.add_singleton_record` in `chia/data_layer/dl_wallet_store.py` executes a path where make `add_singleton_record` apply mirror-linked state changes to a different store, payout target, or pending-root context, violating the invariant that mirror state changes must bind to the intended store and payout-linked singleton state only and leading to Corruption of coin records, lineage, puzzle ownership, offer/trade settlement state, mempool or hint indexes, wallet sync state, pool membership state, or Data Layer root/store state with direct security impact?

## Target
- File/function: chia/data_layer/dl_wallet_store.py:111 `DataLayerStore.add_singleton_record`
- Entrypoint: Data Layer wallet, sync, or store flow reaching `add_singleton_record`
- Attacker controls: mirror identifiers, store ids, urls, payout-linked state, and pending-root timing
- Exploit idea: make `add_singleton_record` apply mirror-linked state changes to a different store, payout target, or pending-root context
- Invariant to test: mirror state changes must bind to the intended store and payout-linked singleton state only
- Expected Immunefi impact: Corruption of coin records, lineage, puzzle ownership, offer/trade settlement state, mempool or hint indexes, wallet sync state, pool membership state, or Data Layer root/store state with direct security impact
- Fast validation: exercise add/delete mirror flows around pending-root changes and assert `chia/data_layer/dl_wallet_store.py:add_singleton_record` binds every effect to the intended store
