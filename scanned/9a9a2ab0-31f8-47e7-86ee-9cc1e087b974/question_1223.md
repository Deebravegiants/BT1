# Q1223: check_subscription_limit loses canonical wallet state after subscription edge cases

## Question
Can an unprivileged attacker reach P2P message handler `check_subscription_limit` and control subscription ids, puzzle hashes, coin ids, and reorg timing so that `FullNodeAPI.check_subscription_limit` in `chia/full_node/full_node_api.py` executes a path where abuse subscription churn around reorg boundaries so `check_subscription_limit` drops or misattributes state that should remain canonical, violating the invariant that subscriptions must not lose or duplicate canonical updates across reorg and replay boundaries and leading to Corruption of coin records, lineage, puzzle ownership, offer/trade settlement state, mempool or hint indexes, wallet sync state, pool membership state, or Data Layer root/store state with direct security impact?

## Target
- File/function: chia/full_node/full_node_api.py:2045 `FullNodeAPI.check_subscription_limit`
- Entrypoint: P2P message handler `check_subscription_limit`
- Attacker controls: subscription ids, puzzle hashes, coin ids, and reorg timing
- Exploit idea: abuse subscription churn around reorg boundaries so `check_subscription_limit` drops or misattributes state that should remain canonical
- Invariant to test: subscriptions must not lose or duplicate canonical updates across reorg and replay boundaries
- Expected Immunefi impact: Corruption of coin records, lineage, puzzle ownership, offer/trade settlement state, mempool or hint indexes, wallet sync state, pool membership state, or Data Layer root/store state with direct security impact
- Fast validation: register/unregister around a reorg in `chia/full_node/full_node_api.py:check_subscription_limit` and assert no canonical coin or puzzle update disappears
