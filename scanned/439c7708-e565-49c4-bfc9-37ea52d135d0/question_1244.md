# Q1244: get_block_spends carries spend state across rollback boundaries

## Question
Can an unprivileged attacker reach RPC route `get_block_spends` and control rollback timing, reorg ordering, and stale mempool or wallet state so that `FullNodeRpcApi.get_block_spends` in `chia/full_node/full_node_rpc_api.py` executes a path where make `get_block_spends` keep attacker-shaped spend state alive across rollback or reorg cleanup, violating the invariant that rollback must remove invalidated spend state completely before any replayed inputs are reconsidered and leading to Corruption of coin records, lineage, puzzle ownership, offer/trade settlement state, mempool or hint indexes, wallet sync state, pool membership state, or Data Layer root/store state with direct security impact?

## Target
- File/function: chia/full_node/full_node_rpc_api.py:502 `FullNodeRpcApi.get_block_spends`
- Entrypoint: RPC route `get_block_spends`
- Attacker controls: rollback timing, reorg ordering, and stale mempool or wallet state
- Exploit idea: make `get_block_spends` keep attacker-shaped spend state alive across rollback or reorg cleanup
- Invariant to test: rollback must remove invalidated spend state completely before any replayed inputs are reconsidered
- Expected Immunefi impact: Corruption of coin records, lineage, puzzle ownership, offer/trade settlement state, mempool or hint indexes, wallet sync state, pool membership state, or Data Layer root/store state with direct security impact
- Fast validation: force rollback around `chia/full_node/full_node_rpc_api.py:get_block_spends` and assert stale spend state is purged before replayed data is reconsidered
