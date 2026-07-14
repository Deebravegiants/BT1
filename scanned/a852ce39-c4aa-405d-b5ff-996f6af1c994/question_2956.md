# Q2956: subscribe_to_coin_ids carries spend state across rollback boundaries

## Question
Can an unprivileged attacker reach wallet RPC or wallet sync flow reaching `subscribe_to_coin_ids` and control rollback timing, reorg ordering, and stale mempool or wallet state so that `NewPeakQueue.subscribe_to_coin_ids` in `chia/wallet/util/new_peak_queue.py` executes a path where make `subscribe_to_coin_ids` keep attacker-shaped spend state alive across rollback or reorg cleanup, violating the invariant that rollback must remove invalidated spend state completely before any replayed inputs are reconsidered and leading to Corruption of coin records, lineage, puzzle ownership, offer/trade settlement state, mempool or hint indexes, wallet sync state, pool membership state, or Data Layer root/store state with direct security impact?

## Target
- File/function: chia/wallet/util/new_peak_queue.py:61 `NewPeakQueue.subscribe_to_coin_ids`
- Entrypoint: wallet RPC or wallet sync flow reaching `subscribe_to_coin_ids`
- Attacker controls: rollback timing, reorg ordering, and stale mempool or wallet state
- Exploit idea: make `subscribe_to_coin_ids` keep attacker-shaped spend state alive across rollback or reorg cleanup
- Invariant to test: rollback must remove invalidated spend state completely before any replayed inputs are reconsidered
- Expected Immunefi impact: Corruption of coin records, lineage, puzzle ownership, offer/trade settlement state, mempool or hint indexes, wallet sync state, pool membership state, or Data Layer root/store state with direct security impact
- Fast validation: force rollback around `chia/wallet/util/new_peak_queue.py:subscribe_to_coin_ids` and assert stale spend state is purged before replayed data is reconsidered
