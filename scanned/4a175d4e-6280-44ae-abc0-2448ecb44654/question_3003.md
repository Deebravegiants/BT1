# Q3003: add_to_additions_in_block loses canonical wallet state after subscription edge cases

## Question
Can an unprivileged attacker reach wallet RPC or wallet sync flow reaching `add_to_additions_in_block` and control subscription ids, puzzle hashes, coin ids, and reorg timing so that `PeerRequestCache.add_to_additions_in_block` in `chia/wallet/util/peer_request_cache.py` executes a path where abuse subscription churn around reorg boundaries so `add_to_additions_in_block` drops or misattributes state that should remain canonical, violating the invariant that subscriptions must not lose or duplicate canonical updates across reorg and replay boundaries and leading to Corruption of coin records, lineage, puzzle ownership, offer/trade settlement state, mempool or hint indexes, wallet sync state, pool membership state, or Data Layer root/store state with direct security impact?

## Target
- File/function: chia/wallet/util/peer_request_cache.py:88 `PeerRequestCache.add_to_additions_in_block`
- Entrypoint: wallet RPC or wallet sync flow reaching `add_to_additions_in_block`
- Attacker controls: subscription ids, puzzle hashes, coin ids, and reorg timing
- Exploit idea: abuse subscription churn around reorg boundaries so `add_to_additions_in_block` drops or misattributes state that should remain canonical
- Invariant to test: subscriptions must not lose or duplicate canonical updates across reorg and replay boundaries
- Expected Immunefi impact: Corruption of coin records, lineage, puzzle ownership, offer/trade settlement state, mempool or hint indexes, wallet sync state, pool membership state, or Data Layer root/store state with direct security impact
- Fast validation: register/unregister around a reorg in `chia/wallet/util/peer_request_cache.py:add_to_additions_in_block` and assert no canonical coin or puzzle update disappears
