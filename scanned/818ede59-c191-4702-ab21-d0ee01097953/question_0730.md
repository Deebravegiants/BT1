# Q730: batch_coin_states_by_puzzle_hashes loses canonical wallet state after subscription edge cases

## Question
Can an unprivileged attacker reach full node mempool, sync, or peer flow reaching `batch_coin_states_by_puzzle_hashes` and control subscription ids, puzzle hashes, coin ids, and reorg timing so that `CoinStore.batch_coin_states_by_puzzle_hashes` in `chia/full_node/coin_store.py` executes a path where abuse subscription churn around reorg boundaries so `batch_coin_states_by_puzzle_hashes` drops or misattributes state that should remain canonical, violating the invariant that subscriptions must not lose or duplicate canonical updates across reorg and replay boundaries and leading to Corruption of coin records, lineage, puzzle ownership, offer/trade settlement state, mempool or hint indexes, wallet sync state, pool membership state, or Data Layer root/store state with direct security impact?

## Target
- File/function: chia/full_node/coin_store.py:451 `CoinStore.batch_coin_states_by_puzzle_hashes`
- Entrypoint: full node mempool, sync, or peer flow reaching `batch_coin_states_by_puzzle_hashes`
- Attacker controls: subscription ids, puzzle hashes, coin ids, and reorg timing
- Exploit idea: abuse subscription churn around reorg boundaries so `batch_coin_states_by_puzzle_hashes` drops or misattributes state that should remain canonical
- Invariant to test: subscriptions must not lose or duplicate canonical updates across reorg and replay boundaries
- Expected Immunefi impact: Corruption of coin records, lineage, puzzle ownership, offer/trade settlement state, mempool or hint indexes, wallet sync state, pool membership state, or Data Layer root/store state with direct security impact
- Fast validation: register/unregister around a reorg in `chia/full_node/coin_store.py:batch_coin_states_by_puzzle_hashes` and assert no canonical coin or puzzle update disappears
