# Q1709: create_waiting_room_inner_puzzle carries spend state across rollback boundaries

## Question
Can an unprivileged attacker reach pool wallet or singleton spend flow reaching `create_waiting_room_inner_puzzle` and control rollback timing, reorg ordering, and stale mempool or wallet state so that `create_waiting_room_inner_puzzle` in `chia/pools/pool_puzzles.py` executes a path where make `create_waiting_room_inner_puzzle` keep attacker-shaped spend state alive across rollback or reorg cleanup, violating the invariant that rollback must remove invalidated spend state completely before any replayed inputs are reconsidered and leading to Corruption of coin records, lineage, puzzle ownership, offer/trade settlement state, mempool or hint indexes, wallet sync state, pool membership state, or Data Layer root/store state with direct security impact?

## Target
- File/function: chia/pools/pool_puzzles.py:51 `create_waiting_room_inner_puzzle`
- Entrypoint: pool wallet or singleton spend flow reaching `create_waiting_room_inner_puzzle`
- Attacker controls: rollback timing, reorg ordering, and stale mempool or wallet state
- Exploit idea: make `create_waiting_room_inner_puzzle` keep attacker-shaped spend state alive across rollback or reorg cleanup
- Invariant to test: rollback must remove invalidated spend state completely before any replayed inputs are reconsidered
- Expected Immunefi impact: Corruption of coin records, lineage, puzzle ownership, offer/trade settlement state, mempool or hint indexes, wallet sync state, pool membership state, or Data Layer root/store state with direct security impact
- Fast validation: force rollback around `chia/pools/pool_puzzles.py:create_waiting_room_inner_puzzle` and assert stale spend state is purged before replayed data is reconsidered
