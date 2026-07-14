# Q3365: add_unacknowledged_coin_state carries spend state across rollback boundaries

## Question
Can an unprivileged attacker reach wallet RPC or wallet sync flow reaching `add_unacknowledged_coin_state` and control rollback timing, reorg ordering, and stale mempool or wallet state so that `WalletInterestedStore.add_unacknowledged_coin_state` in `chia/wallet/wallet_interested_store.py` executes a path where make `add_unacknowledged_coin_state` keep attacker-shaped spend state alive across rollback or reorg cleanup, violating the invariant that rollback must remove invalidated spend state completely before any replayed inputs are reconsidered and leading to Corruption of coin records, lineage, puzzle ownership, offer/trade settlement state, mempool or hint indexes, wallet sync state, pool membership state, or Data Layer root/store state with direct security impact?

## Target
- File/function: chia/wallet/wallet_interested_store.py:128 `WalletInterestedStore.add_unacknowledged_coin_state`
- Entrypoint: wallet RPC or wallet sync flow reaching `add_unacknowledged_coin_state`
- Attacker controls: rollback timing, reorg ordering, and stale mempool or wallet state
- Exploit idea: make `add_unacknowledged_coin_state` keep attacker-shaped spend state alive across rollback or reorg cleanup
- Invariant to test: rollback must remove invalidated spend state completely before any replayed inputs are reconsidered
- Expected Immunefi impact: Corruption of coin records, lineage, puzzle ownership, offer/trade settlement state, mempool or hint indexes, wallet sync state, pool membership state, or Data Layer root/store state with direct security impact
- Fast validation: force rollback around `chia/wallet/wallet_interested_store.py:add_unacknowledged_coin_state` and assert stale spend state is purged before replayed data is reconsidered
