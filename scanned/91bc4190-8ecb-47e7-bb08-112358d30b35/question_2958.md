# Q2958: subscribe_to_coin_ids loses canonical wallet state after subscription edge cases

## Question
Can an unprivileged attacker reach wallet RPC or wallet sync flow reaching `subscribe_to_coin_ids` and control subscription ids, puzzle hashes, coin ids, and reorg timing so that `NewPeakQueue.subscribe_to_coin_ids` in `chia/wallet/util/new_peak_queue.py` executes a path where abuse subscription churn around reorg boundaries so `subscribe_to_coin_ids` drops or misattributes state that should remain canonical, violating the invariant that subscriptions must not lose or duplicate canonical updates across reorg and replay boundaries and leading to Corruption of coin records, lineage, puzzle ownership, offer/trade settlement state, mempool or hint indexes, wallet sync state, pool membership state, or Data Layer root/store state with direct security impact?

## Target
- File/function: chia/wallet/util/new_peak_queue.py:61 `NewPeakQueue.subscribe_to_coin_ids`
- Entrypoint: wallet RPC or wallet sync flow reaching `subscribe_to_coin_ids`
- Attacker controls: subscription ids, puzzle hashes, coin ids, and reorg timing
- Exploit idea: abuse subscription churn around reorg boundaries so `subscribe_to_coin_ids` drops or misattributes state that should remain canonical
- Invariant to test: subscriptions must not lose or duplicate canonical updates across reorg and replay boundaries
- Expected Immunefi impact: Corruption of coin records, lineage, puzzle ownership, offer/trade settlement state, mempool or hint indexes, wallet sync state, pool membership state, or Data Layer root/store state with direct security impact
- Fast validation: register/unregister around a reorg in `chia/wallet/util/new_peak_queue.py:subscribe_to_coin_ids` and assert no canonical coin or puzzle update disappears
