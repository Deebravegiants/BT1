# Q1510: add_subscription loses canonical wallet state after subscription edge cases

## Question
Can an unprivileged attacker reach full node mempool, sync, or peer flow reaching `add_subscription` and control subscription ids, puzzle hashes, coin ids, and reorg timing so that `SubscriptionSet.add_subscription` in `chia/full_node/subscriptions.py` executes a path where abuse subscription churn around reorg boundaries so `add_subscription` drops or misattributes state that should remain canonical, violating the invariant that subscriptions must not lose or duplicate canonical updates across reorg and replay boundaries and leading to Corruption of coin records, lineage, puzzle ownership, offer/trade settlement state, mempool or hint indexes, wallet sync state, pool membership state, or Data Layer root/store state with direct security impact?

## Target
- File/function: chia/full_node/subscriptions.py:18 `SubscriptionSet.add_subscription`
- Entrypoint: full node mempool, sync, or peer flow reaching `add_subscription`
- Attacker controls: subscription ids, puzzle hashes, coin ids, and reorg timing
- Exploit idea: abuse subscription churn around reorg boundaries so `add_subscription` drops or misattributes state that should remain canonical
- Invariant to test: subscriptions must not lose or duplicate canonical updates across reorg and replay boundaries
- Expected Immunefi impact: Corruption of coin records, lineage, puzzle ownership, offer/trade settlement state, mempool or hint indexes, wallet sync state, pool membership state, or Data Layer root/store state with direct security impact
- Fast validation: register/unregister around a reorg in `chia/full_node/subscriptions.py:add_subscription` and assert no canonical coin or puzzle update disappears
