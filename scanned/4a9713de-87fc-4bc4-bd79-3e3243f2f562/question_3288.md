# Q3288: set_finished_sync_up_to loses canonical wallet state after subscription edge cases

## Question
Can an unprivileged attacker reach wallet RPC or wallet sync flow reaching `set_finished_sync_up_to` and control subscription ids, puzzle hashes, coin ids, and reorg timing so that `WalletBlockchain.set_finished_sync_up_to` in `chia/wallet/wallet_blockchain.py` executes a path where abuse subscription churn around reorg boundaries so `set_finished_sync_up_to` drops or misattributes state that should remain canonical, violating the invariant that subscriptions must not lose or duplicate canonical updates across reorg and replay boundaries and leading to Corruption of coin records, lineage, puzzle ownership, offer/trade settlement state, mempool or hint indexes, wallet sync state, pool membership state, or Data Layer root/store state with direct security impact?

## Target
- File/function: chia/wallet/wallet_blockchain.py:197 `WalletBlockchain.set_finished_sync_up_to`
- Entrypoint: wallet RPC or wallet sync flow reaching `set_finished_sync_up_to`
- Attacker controls: subscription ids, puzzle hashes, coin ids, and reorg timing
- Exploit idea: abuse subscription churn around reorg boundaries so `set_finished_sync_up_to` drops or misattributes state that should remain canonical
- Invariant to test: subscriptions must not lose or duplicate canonical updates across reorg and replay boundaries
- Expected Immunefi impact: Corruption of coin records, lineage, puzzle ownership, offer/trade settlement state, mempool or hint indexes, wallet sync state, pool membership state, or Data Layer root/store state with direct security impact
- Fast validation: register/unregister around a reorg in `chia/wallet/wallet_blockchain.py:set_finished_sync_up_to` and assert no canonical coin or puzzle update disappears
