# Q1129: request_puzzle_solution carries spend state across rollback boundaries

## Question
Can an unprivileged attacker reach P2P message handler `request_puzzle_solution` and control rollback timing, reorg ordering, and stale mempool or wallet state so that `FullNodeAPI.request_puzzle_solution` in `chia/full_node/full_node_api.py` executes a path where make `request_puzzle_solution` keep attacker-shaped spend state alive across rollback or reorg cleanup, violating the invariant that rollback must remove invalidated spend state completely before any replayed inputs are reconsidered and leading to Corruption of coin records, lineage, puzzle ownership, offer/trade settlement state, mempool or hint indexes, wallet sync state, pool membership state, or Data Layer root/store state with direct security impact?

## Target
- File/function: chia/full_node/full_node_api.py:1590 `FullNodeAPI.request_puzzle_solution`
- Entrypoint: P2P message handler `request_puzzle_solution`
- Attacker controls: rollback timing, reorg ordering, and stale mempool or wallet state
- Exploit idea: make `request_puzzle_solution` keep attacker-shaped spend state alive across rollback or reorg cleanup
- Invariant to test: rollback must remove invalidated spend state completely before any replayed inputs are reconsidered
- Expected Immunefi impact: Corruption of coin records, lineage, puzzle ownership, offer/trade settlement state, mempool or hint indexes, wallet sync state, pool membership state, or Data Layer root/store state with direct security impact
- Fast validation: force rollback around `chia/full_node/full_node_api.py:request_puzzle_solution` and assert stale spend state is purged before replayed data is reconsidered
