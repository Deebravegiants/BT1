# Q1399: remove_from_pool trusts attacker-shaped state across an internal boundary

## Question
Can an unprivileged attacker reach full node mempool, sync, or peer flow reaching `remove_from_pool` and control security-critical fields that cross from one production layer to another without changing the external attacker model so that `Mempool.remove_from_pool` in `chia/full_node/mempool.py` executes a path where make `remove_from_pool` trust attacker-shaped state that another nearby layer should have revalidated before use, violating the invariant that every boundary between parsing, validation, storage, and execution must revalidate security-critical attacker-controlled fields before trusting them and leading to Corruption of coin records, lineage, puzzle ownership, offer/trade settlement state, mempool or hint indexes, wallet sync state, pool membership state, or Data Layer root/store state with direct security impact?

## Target
- File/function: chia/full_node/mempool.py:347 `Mempool.remove_from_pool`
- Entrypoint: full node mempool, sync, or peer flow reaching `remove_from_pool`
- Attacker controls: security-critical fields that cross from one production layer to another without changing the external attacker model
- Exploit idea: make `remove_from_pool` trust attacker-shaped state that another nearby layer should have revalidated before use
- Invariant to test: every boundary between parsing, validation, storage, and execution must revalidate security-critical attacker-controlled fields before trusting them
- Expected Immunefi impact: Corruption of coin records, lineage, puzzle ownership, offer/trade settlement state, mempool or hint indexes, wallet sync state, pool membership state, or Data Layer root/store state with direct security impact
- Fast validation: drive one attacker-controlled object across adjacent layers into `chia/full_node/mempool.py:remove_from_pool` and assert the receiving layer revalidates every security-critical field before trusting it
