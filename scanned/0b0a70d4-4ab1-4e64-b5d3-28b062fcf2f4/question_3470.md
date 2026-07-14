# Q3470: sync_from_untrusted_close_to_peak loses canonical wallet state after subscription edge cases

## Question
Can an unprivileged attacker reach wallet RPC or wallet sync flow reaching `sync_from_untrusted_close_to_peak` and control subscription ids, puzzle hashes, coin ids, and reorg timing so that `WalletNode.sync_from_untrusted_close_to_peak` in `chia/wallet/wallet_node.py` executes a path where abuse subscription churn around reorg boundaries so `sync_from_untrusted_close_to_peak` drops or misattributes state that should remain canonical, violating the invariant that subscriptions must not lose or duplicate canonical updates across reorg and replay boundaries and leading to Corruption of coin records, lineage, puzzle ownership, offer/trade settlement state, mempool or hint indexes, wallet sync state, pool membership state, or Data Layer root/store state with direct security impact?

## Target
- File/function: chia/wallet/wallet_node.py:1339 `WalletNode.sync_from_untrusted_close_to_peak`
- Entrypoint: wallet RPC or wallet sync flow reaching `sync_from_untrusted_close_to_peak`
- Attacker controls: subscription ids, puzzle hashes, coin ids, and reorg timing
- Exploit idea: abuse subscription churn around reorg boundaries so `sync_from_untrusted_close_to_peak` drops or misattributes state that should remain canonical
- Invariant to test: subscriptions must not lose or duplicate canonical updates across reorg and replay boundaries
- Expected Immunefi impact: Corruption of coin records, lineage, puzzle ownership, offer/trade settlement state, mempool or hint indexes, wallet sync state, pool membership state, or Data Layer root/store state with direct security impact
- Fast validation: register/unregister around a reorg in `chia/wallet/wallet_node.py:sync_from_untrusted_close_to_peak` and assert no canonical coin or puzzle update disappears
