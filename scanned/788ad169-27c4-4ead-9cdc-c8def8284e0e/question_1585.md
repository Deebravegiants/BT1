# Q1585: set_sync_mode replays stale sync messages into live state

## Question
Can an unprivileged attacker reach full node mempool, sync, or peer flow reaching `set_sync_mode` and control stale but protocol-valid sync messages replayed after newer state is present so that `SyncStore.set_sync_mode` in `chia/full_node/sync_store.py` executes a path where replay stale sync objects into `set_sync_mode` after newer canonical state is known and see if they still mutate storage, violating the invariant that stale sync messages must become inert once newer canonical state supersedes them and leading to Corruption of coin records, lineage, puzzle ownership, offer/trade settlement state, mempool or hint indexes, wallet sync state, pool membership state, or Data Layer root/store state with direct security impact?

## Target
- File/function: chia/full_node/sync_store.py:44 `SyncStore.set_sync_mode`
- Entrypoint: full node mempool, sync, or peer flow reaching `set_sync_mode`
- Attacker controls: stale but protocol-valid sync messages replayed after newer state is present
- Exploit idea: replay stale sync objects into `set_sync_mode` after newer canonical state is known and see if they still mutate storage
- Invariant to test: stale sync messages must become inert once newer canonical state supersedes them
- Expected Immunefi impact: Corruption of coin records, lineage, puzzle ownership, offer/trade settlement state, mempool or hint indexes, wallet sync state, pool membership state, or Data Layer root/store state with direct security impact
- Fast validation: replay stale sync messages after newer ones into `chia/full_node/sync_store.py:set_sync_mode` and assert they cannot mutate final stored state
