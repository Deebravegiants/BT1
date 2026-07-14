# Q3682: set_wallet_resync_on_startup loses canonical wallet state after subscription edge cases

## Question
Can an unprivileged attacker reach RPC route `set_wallet_resync_on_startup` and control subscription ids, puzzle hashes, coin ids, and reorg timing so that `WalletRpcApi.set_wallet_resync_on_startup` in `chia/wallet/wallet_rpc_api.py` executes a path where abuse subscription churn around reorg boundaries so `set_wallet_resync_on_startup` drops or misattributes state that should remain canonical, violating the invariant that subscriptions must not lose or duplicate canonical updates across reorg and replay boundaries and leading to Corruption of coin records, lineage, puzzle ownership, offer/trade settlement state, mempool or hint indexes, wallet sync state, pool membership state, or Data Layer root/store state with direct security impact?

## Target
- File/function: chia/wallet/wallet_rpc_api.py:969 `WalletRpcApi.set_wallet_resync_on_startup`
- Entrypoint: RPC route `set_wallet_resync_on_startup`
- Attacker controls: subscription ids, puzzle hashes, coin ids, and reorg timing
- Exploit idea: abuse subscription churn around reorg boundaries so `set_wallet_resync_on_startup` drops or misattributes state that should remain canonical
- Invariant to test: subscriptions must not lose or duplicate canonical updates across reorg and replay boundaries
- Expected Immunefi impact: Corruption of coin records, lineage, puzzle ownership, offer/trade settlement state, mempool or hint indexes, wallet sync state, pool membership state, or Data Layer root/store state with direct security impact
- Fast validation: register/unregister around a reorg in `chia/wallet/wallet_rpc_api.py:set_wallet_resync_on_startup` and assert no canonical coin or puzzle update disappears
