# Q1349: remove_unfinished_block trusts attacker-shaped state across an internal boundary

## Question
Can an unprivileged attacker reach full node mempool, sync, or peer flow reaching `remove_unfinished_block` and control security-critical fields that cross from one production layer to another without changing the external attacker model so that `FullNodeStore.remove_unfinished_block` in `chia/full_node/full_node_store.py` executes a path where make `remove_unfinished_block` trust attacker-shaped state that another nearby layer should have revalidated before use, violating the invariant that every boundary between parsing, validation, storage, and execution must revalidate security-critical attacker-controlled fields before trusting them and leading to Corruption of coin records, lineage, puzzle ownership, offer/trade settlement state, mempool or hint indexes, wallet sync state, pool membership state, or Data Layer root/store state with direct security impact?

## Target
- File/function: chia/full_node/full_node_store.py:373 `FullNodeStore.remove_unfinished_block`
- Entrypoint: full node mempool, sync, or peer flow reaching `remove_unfinished_block`
- Attacker controls: security-critical fields that cross from one production layer to another without changing the external attacker model
- Exploit idea: make `remove_unfinished_block` trust attacker-shaped state that another nearby layer should have revalidated before use
- Invariant to test: every boundary between parsing, validation, storage, and execution must revalidate security-critical attacker-controlled fields before trusting them
- Expected Immunefi impact: Corruption of coin records, lineage, puzzle ownership, offer/trade settlement state, mempool or hint indexes, wallet sync state, pool membership state, or Data Layer root/store state with direct security impact
- Fast validation: drive one attacker-controlled object across adjacent layers into `chia/full_node/full_node_store.py:remove_unfinished_block` and assert the receiving layer revalidates every security-critical field before trusting it
