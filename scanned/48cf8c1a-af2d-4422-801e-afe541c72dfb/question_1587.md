# Q1587: set_long_sync corrupts sync state under reordered peer updates

## Question
Can an unprivileged attacker reach full node mempool, sync, or peer flow reaching `set_long_sync` and control reordered peer updates, stale heights, and inconsistent state snapshots so that `SyncStore.set_long_sync` in `chia/full_node/sync_store.py` executes a path where feed `set_long_sync` stale and fresh sync data in attacker-chosen order until the stored wallet or node view becomes non-canonical, violating the invariant that the canonical sync view must converge regardless of attacker-controlled delivery order among valid messages and leading to Corruption of coin records, lineage, puzzle ownership, offer/trade settlement state, mempool or hint indexes, wallet sync state, pool membership state, or Data Layer root/store state with direct security impact?

## Target
- File/function: chia/full_node/sync_store.py:50 `SyncStore.set_long_sync`
- Entrypoint: full node mempool, sync, or peer flow reaching `set_long_sync`
- Attacker controls: reordered peer updates, stale heights, and inconsistent state snapshots
- Exploit idea: feed `set_long_sync` stale and fresh sync data in attacker-chosen order until the stored wallet or node view becomes non-canonical
- Invariant to test: the canonical sync view must converge regardless of attacker-controlled delivery order among valid messages
- Expected Immunefi impact: Corruption of coin records, lineage, puzzle ownership, offer/trade settlement state, mempool or hint indexes, wallet sync state, pool membership state, or Data Layer root/store state with direct security impact
- Fast validation: reorder valid sync messages into `chia/full_node/sync_store.py:set_long_sync` and assert the final stored state matches canonical chain order
