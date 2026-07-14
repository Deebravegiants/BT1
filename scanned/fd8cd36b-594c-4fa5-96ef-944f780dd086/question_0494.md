# Q494: select_coins redirects or misbinds Data Layer mirror state

## Question
Can an unprivileged attacker reach Data Layer wallet, sync, or store flow reaching `select_coins` and control mirror identifiers, store ids, urls, payout-linked state, and pending-root timing so that `DataLayerWallet.select_coins` in `chia/data_layer/data_layer_wallet.py` executes a path where make `select_coins` apply mirror-linked state changes to a different store, payout target, or pending-root context, violating the invariant that mirror state changes must bind to the intended store and payout-linked singleton state only and leading to Corruption of coin records, lineage, puzzle ownership, offer/trade settlement state, mempool or hint indexes, wallet sync state, pool membership state, or Data Layer root/store state with direct security impact?

## Target
- File/function: chia/data_layer/data_layer_wallet.py:1212 `DataLayerWallet.select_coins`
- Entrypoint: Data Layer wallet, sync, or store flow reaching `select_coins`
- Attacker controls: mirror identifiers, store ids, urls, payout-linked state, and pending-root timing
- Exploit idea: make `select_coins` apply mirror-linked state changes to a different store, payout target, or pending-root context
- Invariant to test: mirror state changes must bind to the intended store and payout-linked singleton state only
- Expected Immunefi impact: Corruption of coin records, lineage, puzzle ownership, offer/trade settlement state, mempool or hint indexes, wallet sync state, pool membership state, or Data Layer root/store state with direct security impact
- Fast validation: exercise add/delete mirror flows around pending-root changes and assert `chia/data_layer/data_layer_wallet.py:select_coins` binds every effect to the intended store
