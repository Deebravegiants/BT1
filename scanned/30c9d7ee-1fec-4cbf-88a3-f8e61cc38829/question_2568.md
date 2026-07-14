# Q2568: solve_puzzle carries spend state across rollback boundaries

## Question
Can an unprivileged attacker reach wallet RPC or wallet sync flow reaching `solve_puzzle` and control rollback timing, reorg ordering, and stale mempool or wallet state so that `solve_puzzle` in `chia/wallet/outer_puzzles.py` executes a path where make `solve_puzzle` keep attacker-shaped spend state alive across rollback or reorg cleanup, violating the invariant that rollback must remove invalidated spend state completely before any replayed inputs are reconsidered and leading to Corruption of coin records, lineage, puzzle ownership, offer/trade settlement state, mempool or hint indexes, wallet sync state, pool membership state, or Data Layer root/store state with direct security impact?

## Target
- File/function: chia/wallet/outer_puzzles.py:61 `solve_puzzle`
- Entrypoint: wallet RPC or wallet sync flow reaching `solve_puzzle`
- Attacker controls: rollback timing, reorg ordering, and stale mempool or wallet state
- Exploit idea: make `solve_puzzle` keep attacker-shaped spend state alive across rollback or reorg cleanup
- Invariant to test: rollback must remove invalidated spend state completely before any replayed inputs are reconsidered
- Expected Immunefi impact: Corruption of coin records, lineage, puzzle ownership, offer/trade settlement state, mempool or hint indexes, wallet sync state, pool membership state, or Data Layer root/store state with direct security impact
- Fast validation: force rollback around `chia/wallet/outer_puzzles.py:solve_puzzle` and assert stale spend state is purged before replayed data is reconsidered
