# Q556: rollback_to_block cross-contaminates multiple Data Layer stores

## Question
Can an unprivileged attacker reach Data Layer wallet, sync, or store flow reaching `rollback_to_block` and control batched updates across multiple store ids and roots so that `DataLayerStore.rollback_to_block` in `chia/data_layer/dl_wallet_store.py` executes a path where make `rollback_to_block` commit part of a multi-store update under the wrong root or wrong store id, violating the invariant that batched Data Layer updates must be atomic per stated store set and root set and leading to Corruption of coin records, lineage, puzzle ownership, offer/trade settlement state, mempool or hint indexes, wallet sync state, pool membership state, or Data Layer root/store state with direct security impact?

## Target
- File/function: chia/data_layer/dl_wallet_store.py:374 `DataLayerStore.rollback_to_block`
- Entrypoint: Data Layer wallet, sync, or store flow reaching `rollback_to_block`
- Attacker controls: batched updates across multiple store ids and roots
- Exploit idea: make `rollback_to_block` commit part of a multi-store update under the wrong root or wrong store id
- Invariant to test: batched Data Layer updates must be atomic per stated store set and root set
- Expected Immunefi impact: Corruption of coin records, lineage, puzzle ownership, offer/trade settlement state, mempool or hint indexes, wallet sync state, pool membership state, or Data Layer root/store state with direct security impact
- Fast validation: inject a partial-failure batched update into `chia/data_layer/dl_wallet_store.py:rollback_to_block` and assert no store commits under the wrong root
