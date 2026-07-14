# Q1112: request_removals loses canonical wallet state after subscription edge cases

## Question
Can an unprivileged attacker reach P2P message handler `request_removals` and control subscription ids, puzzle hashes, coin ids, and reorg timing so that `FullNodeAPI.request_removals` in `chia/full_node/full_node_api.py` executes a path where abuse subscription churn around reorg boundaries so `request_removals` drops or misattributes state that should remain canonical, violating the invariant that subscriptions must not lose or duplicate canonical updates across reorg and replay boundaries and leading to Corruption of coin records, lineage, puzzle ownership, offer/trade settlement state, mempool or hint indexes, wallet sync state, pool membership state, or Data Layer root/store state with direct security impact?

## Target
- File/function: chia/full_node/full_node_api.py:1474 `FullNodeAPI.request_removals`
- Entrypoint: P2P message handler `request_removals`
- Attacker controls: subscription ids, puzzle hashes, coin ids, and reorg timing
- Exploit idea: abuse subscription churn around reorg boundaries so `request_removals` drops or misattributes state that should remain canonical
- Invariant to test: subscriptions must not lose or duplicate canonical updates across reorg and replay boundaries
- Expected Immunefi impact: Corruption of coin records, lineage, puzzle ownership, offer/trade settlement state, mempool or hint indexes, wallet sync state, pool membership state, or Data Layer root/store state with direct security impact
- Fast validation: register/unregister around a reorg in `chia/full_node/full_node_api.py:request_removals` and assert no canonical coin or puzzle update disappears
