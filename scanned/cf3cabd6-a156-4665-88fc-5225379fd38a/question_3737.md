# Q3737: send_transaction_multi carries spend state across rollback boundaries

## Question
Can an unprivileged attacker reach RPC route `send_transaction_multi` and control rollback timing, reorg ordering, and stale mempool or wallet state so that `WalletRpcApi.send_transaction_multi` in `chia/wallet/wallet_rpc_api.py` executes a path where make `send_transaction_multi` keep attacker-shaped spend state alive across rollback or reorg cleanup, violating the invariant that rollback must remove invalidated spend state completely before any replayed inputs are reconsidered and leading to Corruption of coin records, lineage, puzzle ownership, offer/trade settlement state, mempool or hint indexes, wallet sync state, pool membership state, or Data Layer root/store state with direct security impact?

## Target
- File/function: chia/wallet/wallet_rpc_api.py:1567 `WalletRpcApi.send_transaction_multi`
- Entrypoint: RPC route `send_transaction_multi`
- Attacker controls: rollback timing, reorg ordering, and stale mempool or wallet state
- Exploit idea: make `send_transaction_multi` keep attacker-shaped spend state alive across rollback or reorg cleanup
- Invariant to test: rollback must remove invalidated spend state completely before any replayed inputs are reconsidered
- Expected Immunefi impact: Corruption of coin records, lineage, puzzle ownership, offer/trade settlement state, mempool or hint indexes, wallet sync state, pool membership state, or Data Layer root/store state with direct security impact
- Fast validation: force rollback around `chia/wallet/wallet_rpc_api.py:send_transaction_multi` and assert stale spend state is purged before replayed data is reconsidered
