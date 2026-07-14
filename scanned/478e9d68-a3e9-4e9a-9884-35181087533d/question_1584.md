# Q1584: set_sync_mode loses canonical wallet state after subscription edge cases

## Question
Can an unprivileged attacker reach full node mempool, sync, or peer flow reaching `set_sync_mode` and control subscription ids, puzzle hashes, coin ids, and reorg timing so that `SyncStore.set_sync_mode` in `chia/full_node/sync_store.py` executes a path where abuse subscription churn around reorg boundaries so `set_sync_mode` drops or misattributes state that should remain canonical, violating the invariant that subscriptions must not lose or duplicate canonical updates across reorg and replay boundaries and leading to Corruption of coin records, lineage, puzzle ownership, offer/trade settlement state, mempool or hint indexes, wallet sync state, pool membership state, or Data Layer root/store state with direct security impact?

## Target
- File/function: chia/full_node/sync_store.py:44 `SyncStore.set_sync_mode`
- Entrypoint: full node mempool, sync, or peer flow reaching `set_sync_mode`
- Attacker controls: subscription ids, puzzle hashes, coin ids, and reorg timing
- Exploit idea: abuse subscription churn around reorg boundaries so `set_sync_mode` drops or misattributes state that should remain canonical
- Invariant to test: subscriptions must not lose or duplicate canonical updates across reorg and replay boundaries
- Expected Immunefi impact: Corruption of coin records, lineage, puzzle ownership, offer/trade settlement state, mempool or hint indexes, wallet sync state, pool membership state, or Data Layer root/store state with direct security impact
- Fast validation: register/unregister around a reorg in `chia/full_node/sync_store.py:set_sync_mode` and assert no canonical coin or puzzle update disappears
