# Q461: stop_tracking_singleton cross-contaminates multiple Data Layer stores

## Question
Can an unprivileged attacker reach Data Layer wallet, sync, or store flow reaching `stop_tracking_singleton` and control batched updates across multiple store ids and roots so that `DataLayerWallet.stop_tracking_singleton` in `chia/data_layer/data_layer_wallet.py` executes a path where make `stop_tracking_singleton` commit part of a multi-store update under the wrong root or wrong store id, violating the invariant that batched Data Layer updates must be atomic per stated store set and root set and leading to Corruption of coin records, lineage, puzzle ownership, offer/trade settlement state, mempool or hint indexes, wallet sync state, pool membership state, or Data Layer root/store state with direct security impact?

## Target
- File/function: chia/data_layer/data_layer_wallet.py:868 `DataLayerWallet.stop_tracking_singleton`
- Entrypoint: Data Layer wallet, sync, or store flow reaching `stop_tracking_singleton`
- Attacker controls: batched updates across multiple store ids and roots
- Exploit idea: make `stop_tracking_singleton` commit part of a multi-store update under the wrong root or wrong store id
- Invariant to test: batched Data Layer updates must be atomic per stated store set and root set
- Expected Immunefi impact: Corruption of coin records, lineage, puzzle ownership, offer/trade settlement state, mempool or hint indexes, wallet sync state, pool membership state, or Data Layer root/store state with direct security impact
- Fast validation: inject a partial-failure batched update into `chia/data_layer/data_layer_wallet.py:stop_tracking_singleton` and assert no store commits under the wrong root
