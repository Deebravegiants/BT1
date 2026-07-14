# Q1558: remove_coin_subscriptions loses canonical wallet state after subscription edge cases

## Question
Can an unprivileged attacker reach full node mempool, sync, or peer flow reaching `remove_coin_subscriptions` and control subscription ids, puzzle hashes, coin ids, and reorg timing so that `PeerSubscriptions.remove_coin_subscriptions` in `chia/full_node/subscriptions.py` executes a path where abuse subscription churn around reorg boundaries so `remove_coin_subscriptions` drops or misattributes state that should remain canonical, violating the invariant that subscriptions must not lose or duplicate canonical updates across reorg and replay boundaries and leading to Corruption of coin records, lineage, puzzle ownership, offer/trade settlement state, mempool or hint indexes, wallet sync state, pool membership state, or Data Layer root/store state with direct security impact?

## Target
- File/function: chia/full_node/subscriptions.py:170 `PeerSubscriptions.remove_coin_subscriptions`
- Entrypoint: full node mempool, sync, or peer flow reaching `remove_coin_subscriptions`
- Attacker controls: subscription ids, puzzle hashes, coin ids, and reorg timing
- Exploit idea: abuse subscription churn around reorg boundaries so `remove_coin_subscriptions` drops or misattributes state that should remain canonical
- Invariant to test: subscriptions must not lose or duplicate canonical updates across reorg and replay boundaries
- Expected Immunefi impact: Corruption of coin records, lineage, puzzle ownership, offer/trade settlement state, mempool or hint indexes, wallet sync state, pool membership state, or Data Layer root/store state with direct security impact
- Fast validation: register/unregister around a reorg in `chia/full_node/subscriptions.py:remove_coin_subscriptions` and assert no canonical coin or puzzle update disappears
