# Q3825: register_remote_coins carries spend state across rollback boundaries

## Question
Can an unprivileged attacker reach RPC route `register_remote_coins` and control rollback timing, reorg ordering, and stale mempool or wallet state so that `WalletRpcApi.register_remote_coins` in `chia/wallet/wallet_rpc_api.py` executes a path where make `register_remote_coins` keep attacker-shaped spend state alive across rollback or reorg cleanup, violating the invariant that rollback must remove invalidated spend state completely before any replayed inputs are reconsidered and leading to Corruption of coin records, lineage, puzzle ownership, offer/trade settlement state, mempool or hint indexes, wallet sync state, pool membership state, or Data Layer root/store state with direct security impact?

## Target
- File/function: chia/wallet/wallet_rpc_api.py:3038 `WalletRpcApi.register_remote_coins`
- Entrypoint: RPC route `register_remote_coins`
- Attacker controls: rollback timing, reorg ordering, and stale mempool or wallet state
- Exploit idea: make `register_remote_coins` keep attacker-shaped spend state alive across rollback or reorg cleanup
- Invariant to test: rollback must remove invalidated spend state completely before any replayed inputs are reconsidered
- Expected Immunefi impact: Corruption of coin records, lineage, puzzle ownership, offer/trade settlement state, mempool or hint indexes, wallet sync state, pool membership state, or Data Layer root/store state with direct security impact
- Fast validation: force rollback around `chia/wallet/wallet_rpc_api.py:register_remote_coins` and assert stale spend state is purged before replayed data is reconsidered
