# Q3032: request_header_blocks loses canonical wallet state after subscription edge cases

## Question
Can an unprivileged attacker reach wallet RPC or wallet sync flow reaching `request_header_blocks` and control subscription ids, puzzle hashes, coin ids, and reorg timing so that `request_header_blocks` in `chia/wallet/util/wallet_sync_utils.py` executes a path where abuse subscription churn around reorg boundaries so `request_header_blocks` drops or misattributes state that should remain canonical, violating the invariant that subscriptions must not lose or duplicate canonical updates across reorg and replay boundaries and leading to Corruption of coin records, lineage, puzzle ownership, offer/trade settlement state, mempool or hint indexes, wallet sync state, pool membership state, or Data Layer root/store state with direct security impact?

## Target
- File/function: chia/wallet/util/wallet_sync_utils.py:248 `request_header_blocks`
- Entrypoint: wallet RPC or wallet sync flow reaching `request_header_blocks`
- Attacker controls: subscription ids, puzzle hashes, coin ids, and reorg timing
- Exploit idea: abuse subscription churn around reorg boundaries so `request_header_blocks` drops or misattributes state that should remain canonical
- Invariant to test: subscriptions must not lose or duplicate canonical updates across reorg and replay boundaries
- Expected Immunefi impact: Corruption of coin records, lineage, puzzle ownership, offer/trade settlement state, mempool or hint indexes, wallet sync state, pool membership state, or Data Layer root/store state with direct security impact
- Fast validation: register/unregister around a reorg in `chia/wallet/util/wallet_sync_utils.py:request_header_blocks` and assert no canonical coin or puzzle update disappears
