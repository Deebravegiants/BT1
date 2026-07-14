# Q1296: get_mempool_item_by_tx_id carries spend state across rollback boundaries

## Question
Can an unprivileged attacker reach RPC route `get_mempool_item_by_tx_id` and control rollback timing, reorg ordering, and stale mempool or wallet state so that `FullNodeRpcApi.get_mempool_item_by_tx_id` in `chia/full_node/full_node_rpc_api.py` executes a path where make `get_mempool_item_by_tx_id` keep attacker-shaped spend state alive across rollback or reorg cleanup, violating the invariant that rollback must remove invalidated spend state completely before any replayed inputs are reconsidered and leading to Corruption of coin records, lineage, puzzle ownership, offer/trade settlement state, mempool or hint indexes, wallet sync state, pool membership state, or Data Layer root/store state with direct security impact?

## Target
- File/function: chia/full_node/full_node_rpc_api.py:941 `FullNodeRpcApi.get_mempool_item_by_tx_id`
- Entrypoint: RPC route `get_mempool_item_by_tx_id`
- Attacker controls: rollback timing, reorg ordering, and stale mempool or wallet state
- Exploit idea: make `get_mempool_item_by_tx_id` keep attacker-shaped spend state alive across rollback or reorg cleanup
- Invariant to test: rollback must remove invalidated spend state completely before any replayed inputs are reconsidered
- Expected Immunefi impact: Corruption of coin records, lineage, puzzle ownership, offer/trade settlement state, mempool or hint indexes, wallet sync state, pool membership state, or Data Layer root/store state with direct security impact
- Fast validation: force rollback around `chia/full_node/full_node_rpc_api.py:get_mempool_item_by_tx_id` and assert stale spend state is purged before replayed data is reconsidered
