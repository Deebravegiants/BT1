# Q2967: subscribe_to_puzzle_hashes carries spend state across rollback boundaries

## Question
Can an unprivileged attacker reach wallet RPC or wallet sync flow reaching `subscribe_to_puzzle_hashes` and control rollback timing, reorg ordering, and stale mempool or wallet state so that `NewPeakQueue.subscribe_to_puzzle_hashes` in `chia/wallet/util/new_peak_queue.py` executes a path where make `subscribe_to_puzzle_hashes` keep attacker-shaped spend state alive across rollback or reorg cleanup, violating the invariant that rollback must remove invalidated spend state completely before any replayed inputs are reconsidered and leading to Corruption of coin records, lineage, puzzle ownership, offer/trade settlement state, mempool or hint indexes, wallet sync state, pool membership state, or Data Layer root/store state with direct security impact?

## Target
- File/function: chia/wallet/util/new_peak_queue.py:65 `NewPeakQueue.subscribe_to_puzzle_hashes`
- Entrypoint: wallet RPC or wallet sync flow reaching `subscribe_to_puzzle_hashes`
- Attacker controls: rollback timing, reorg ordering, and stale mempool or wallet state
- Exploit idea: make `subscribe_to_puzzle_hashes` keep attacker-shaped spend state alive across rollback or reorg cleanup
- Invariant to test: rollback must remove invalidated spend state completely before any replayed inputs are reconsidered
- Expected Immunefi impact: Corruption of coin records, lineage, puzzle ownership, offer/trade settlement state, mempool or hint indexes, wallet sync state, pool membership state, or Data Layer root/store state with direct security impact
- Fast validation: force rollback around `chia/wallet/util/new_peak_queue.py:subscribe_to_puzzle_hashes` and assert stale spend state is purged before replayed data is reconsidered
