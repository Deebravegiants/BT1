# Q820: sync_from_fork_point trusts attacker-shaped state across an internal boundary

## Question
Can an unprivileged attacker reach full node mempool, sync, or peer flow reaching `sync_from_fork_point` and control security-critical fields that cross from one production layer to another without changing the external attacker model so that `FullNode.sync_from_fork_point` in `chia/full_node/full_node.py` executes a path where make `sync_from_fork_point` trust attacker-shaped state that another nearby layer should have revalidated before use, violating the invariant that every boundary between parsing, validation, storage, and execution must revalidate security-critical attacker-controlled fields before trusting them and leading to Corruption of coin records, lineage, puzzle ownership, offer/trade settlement state, mempool or hint indexes, wallet sync state, pool membership state, or Data Layer root/store state with direct security impact?

## Target
- File/function: chia/full_node/full_node.py:1196 `FullNode.sync_from_fork_point`
- Entrypoint: full node mempool, sync, or peer flow reaching `sync_from_fork_point`
- Attacker controls: security-critical fields that cross from one production layer to another without changing the external attacker model
- Exploit idea: make `sync_from_fork_point` trust attacker-shaped state that another nearby layer should have revalidated before use
- Invariant to test: every boundary between parsing, validation, storage, and execution must revalidate security-critical attacker-controlled fields before trusting them
- Expected Immunefi impact: Corruption of coin records, lineage, puzzle ownership, offer/trade settlement state, mempool or hint indexes, wallet sync state, pool membership state, or Data Layer root/store state with direct security impact
- Fast validation: drive one attacker-controlled object across adjacent layers into `chia/full_node/full_node.py:sync_from_fork_point` and assert the receiving layer revalidates every security-critical field before trusting it
