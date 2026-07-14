# Q1111: request_removals corrupts sync state under reordered peer updates

## Question
Can an unprivileged attacker reach P2P message handler `request_removals` and control reordered peer updates, stale heights, and inconsistent state snapshots so that `FullNodeAPI.request_removals` in `chia/full_node/full_node_api.py` executes a path where feed `request_removals` stale and fresh sync data in attacker-chosen order until the stored wallet or node view becomes non-canonical, violating the invariant that the canonical sync view must converge regardless of attacker-controlled delivery order among valid messages and leading to Corruption of coin records, lineage, puzzle ownership, offer/trade settlement state, mempool or hint indexes, wallet sync state, pool membership state, or Data Layer root/store state with direct security impact?

## Target
- File/function: chia/full_node/full_node_api.py:1474 `FullNodeAPI.request_removals`
- Entrypoint: P2P message handler `request_removals`
- Attacker controls: reordered peer updates, stale heights, and inconsistent state snapshots
- Exploit idea: feed `request_removals` stale and fresh sync data in attacker-chosen order until the stored wallet or node view becomes non-canonical
- Invariant to test: the canonical sync view must converge regardless of attacker-controlled delivery order among valid messages
- Expected Immunefi impact: Corruption of coin records, lineage, puzzle ownership, offer/trade settlement state, mempool or hint indexes, wallet sync state, pool membership state, or Data Layer root/store state with direct security impact
- Fast validation: reorder valid sync messages into `chia/full_node/full_node_api.py:request_removals` and assert the final stored state matches canonical chain order
