# Q2846: add_coin_ids carries spend state across rollback boundaries

## Question
Can an unprivileged attacker reach wallet RPC or wallet sync flow reaching `add_coin_ids` and control rollback timing, reorg ordering, and stale mempool or wallet state so that `RemoteCoinStore.add_coin_ids` in `chia/wallet/remote_wallet/remote_coin_store.py` executes a path where make `add_coin_ids` keep attacker-shaped spend state alive across rollback or reorg cleanup, violating the invariant that rollback must remove invalidated spend state completely before any replayed inputs are reconsidered and leading to Corruption of coin records, lineage, puzzle ownership, offer/trade settlement state, mempool or hint indexes, wallet sync state, pool membership state, or Data Layer root/store state with direct security impact?

## Target
- File/function: chia/wallet/remote_wallet/remote_coin_store.py:27 `RemoteCoinStore.add_coin_ids`
- Entrypoint: wallet RPC or wallet sync flow reaching `add_coin_ids`
- Attacker controls: rollback timing, reorg ordering, and stale mempool or wallet state
- Exploit idea: make `add_coin_ids` keep attacker-shaped spend state alive across rollback or reorg cleanup
- Invariant to test: rollback must remove invalidated spend state completely before any replayed inputs are reconsidered
- Expected Immunefi impact: Corruption of coin records, lineage, puzzle ownership, offer/trade settlement state, mempool or hint indexes, wallet sync state, pool membership state, or Data Layer root/store state with direct security impact
- Fast validation: force rollback around `chia/wallet/remote_wallet/remote_coin_store.py:add_coin_ids` and assert stale spend state is purged before replayed data is reconsidered
