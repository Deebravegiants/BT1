# Q495: select_coins reuses pending-root state after the security context changed

## Question
Can an unprivileged attacker reach Data Layer wallet, sync, or store flow reaching `select_coins` and control pending roots, clear/cancel timing, and subsequent root submissions so that `DataLayerWallet.select_coins` in `chia/data_layer/data_layer_wallet.py` executes a path where make `select_coins` reuse pending-root authority after the store's canonical security context changed, violating the invariant that pending-root state must expire when the canonical store security context no longer matches it and leading to Corruption of coin records, lineage, puzzle ownership, offer/trade settlement state, mempool or hint indexes, wallet sync state, pool membership state, or Data Layer root/store state with direct security impact?

## Target
- File/function: chia/data_layer/data_layer_wallet.py:1212 `DataLayerWallet.select_coins`
- Entrypoint: Data Layer wallet, sync, or store flow reaching `select_coins`
- Attacker controls: pending roots, clear/cancel timing, and subsequent root submissions
- Exploit idea: make `select_coins` reuse pending-root authority after the store's canonical security context changed
- Invariant to test: pending-root state must expire when the canonical store security context no longer matches it
- Expected Immunefi impact: Corruption of coin records, lineage, puzzle ownership, offer/trade settlement state, mempool or hint indexes, wallet sync state, pool membership state, or Data Layer root/store state with direct security impact
- Fast validation: mutate canonical store context between pending-root creation and submit in `chia/data_layer/data_layer_wallet.py:select_coins` and assert stale pending roots die cleanly
