# Q3020: subscribe_to_coin_updates carries spend state across rollback boundaries

## Question
Can an unprivileged attacker reach wallet RPC or wallet sync flow reaching `subscribe_to_coin_updates` and control rollback timing, reorg ordering, and stale mempool or wallet state so that `subscribe_to_coin_updates` in `chia/wallet/util/wallet_sync_utils.py` executes a path where make `subscribe_to_coin_updates` keep attacker-shaped spend state alive across rollback or reorg cleanup, violating the invariant that rollback must remove invalidated spend state completely before any replayed inputs are reconsidered and leading to Corruption of coin records, lineage, puzzle ownership, offer/trade settlement state, mempool or hint indexes, wallet sync state, pool membership state, or Data Layer root/store state with direct security impact?

## Target
- File/function: chia/wallet/util/wallet_sync_utils.py:72 `subscribe_to_coin_updates`
- Entrypoint: wallet RPC or wallet sync flow reaching `subscribe_to_coin_updates`
- Attacker controls: rollback timing, reorg ordering, and stale mempool or wallet state
- Exploit idea: make `subscribe_to_coin_updates` keep attacker-shaped spend state alive across rollback or reorg cleanup
- Invariant to test: rollback must remove invalidated spend state completely before any replayed inputs are reconsidered
- Expected Immunefi impact: Corruption of coin records, lineage, puzzle ownership, offer/trade settlement state, mempool or hint indexes, wallet sync state, pool membership state, or Data Layer root/store state with direct security impact
- Fast validation: force rollback around `chia/wallet/util/wallet_sync_utils.py:subscribe_to_coin_updates` and assert stale spend state is purged before replayed data is reconsidered
