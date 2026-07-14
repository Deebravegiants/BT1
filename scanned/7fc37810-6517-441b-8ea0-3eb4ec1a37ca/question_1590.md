# Q1590: set_long_sync trusts attacker-shaped state across an internal boundary

## Question
Can an unprivileged attacker reach full node mempool, sync, or peer flow reaching `set_long_sync` and control security-critical fields that cross from one production layer to another without changing the external attacker model so that `SyncStore.set_long_sync` in `chia/full_node/sync_store.py` executes a path where make `set_long_sync` trust attacker-shaped state that another nearby layer should have revalidated before use, violating the invariant that every boundary between parsing, validation, storage, and execution must revalidate security-critical attacker-controlled fields before trusting them and leading to Corruption of coin records, lineage, puzzle ownership, offer/trade settlement state, mempool or hint indexes, wallet sync state, pool membership state, or Data Layer root/store state with direct security impact?

## Target
- File/function: chia/full_node/sync_store.py:50 `SyncStore.set_long_sync`
- Entrypoint: full node mempool, sync, or peer flow reaching `set_long_sync`
- Attacker controls: security-critical fields that cross from one production layer to another without changing the external attacker model
- Exploit idea: make `set_long_sync` trust attacker-shaped state that another nearby layer should have revalidated before use
- Invariant to test: every boundary between parsing, validation, storage, and execution must revalidate security-critical attacker-controlled fields before trusting them
- Expected Immunefi impact: Corruption of coin records, lineage, puzzle ownership, offer/trade settlement state, mempool or hint indexes, wallet sync state, pool membership state, or Data Layer root/store state with direct security impact
- Fast validation: drive one attacker-controlled object across adjacent layers into `chia/full_node/sync_store.py:set_long_sync` and assert the receiving layer revalidates every security-critical field before trusting it
