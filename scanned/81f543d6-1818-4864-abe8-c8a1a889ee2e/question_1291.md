# Q1291: get_mempool_item_by_tx_id replays attacker-controlled spends across cache or reorg boundaries

## Question
Can an unprivileged attacker reach RPC route `get_mempool_item_by_tx_id` and control replayed bundles, reordered peer deliveries, and reorg timing so that `FullNodeRpcApi.get_mempool_item_by_tx_id` in `chia/full_node/full_node_rpc_api.py` executes a path where use replay or rollback ordering so `get_mempool_item_by_tx_id` resurrects attacker-chosen spend state after it should be dead, violating the invariant that once a spend path is invalidated by confirmation, rollback, or conflict resolution, it must not silently become active again and leading to Consensus divergence, deterministic validation mismatch, invalid block or spend acceptance, forged weight proof trust, or chain halt caused by an unprivileged block, spend bundle, protocol message, sync path, or mempool interaction?

## Target
- File/function: chia/full_node/full_node_rpc_api.py:941 `FullNodeRpcApi.get_mempool_item_by_tx_id`
- Entrypoint: RPC route `get_mempool_item_by_tx_id`
- Attacker controls: replayed bundles, reordered peer deliveries, and reorg timing
- Exploit idea: use replay or rollback ordering so `get_mempool_item_by_tx_id` resurrects attacker-chosen spend state after it should be dead
- Invariant to test: once a spend path is invalidated by confirmation, rollback, or conflict resolution, it must not silently become active again
- Expected Immunefi impact: Consensus divergence, deterministic validation mismatch, invalid block or spend acceptance, forged weight proof trust, or chain halt caused by an unprivileged block, spend bundle, protocol message, sync path, or mempool interaction
- Fast validation: replay the same attacker-crafted spend or wallet state across rollback/reorg test steps and assert `get_mempool_item_by_tx_id` never reactivates stale state
