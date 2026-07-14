# Q417: create_update_state_spend carries spend state across rollback boundaries

## Question
Can an unprivileged attacker reach Data Layer wallet, sync, or store flow reaching `create_update_state_spend` and control rollback timing, reorg ordering, and stale mempool or wallet state so that `DataLayerWallet.create_update_state_spend` in `chia/data_layer/data_layer_wallet.py` executes a path where make `create_update_state_spend` keep attacker-shaped spend state alive across rollback or reorg cleanup, violating the invariant that rollback must remove invalidated spend state completely before any replayed inputs are reconsidered and leading to Corruption of coin records, lineage, puzzle ownership, offer/trade settlement state, mempool or hint indexes, wallet sync state, pool membership state, or Data Layer root/store state with direct security impact?

## Target
- File/function: chia/data_layer/data_layer_wallet.py:382 `DataLayerWallet.create_update_state_spend`
- Entrypoint: Data Layer wallet, sync, or store flow reaching `create_update_state_spend`
- Attacker controls: rollback timing, reorg ordering, and stale mempool or wallet state
- Exploit idea: make `create_update_state_spend` keep attacker-shaped spend state alive across rollback or reorg cleanup
- Invariant to test: rollback must remove invalidated spend state completely before any replayed inputs are reconsidered
- Expected Immunefi impact: Corruption of coin records, lineage, puzzle ownership, offer/trade settlement state, mempool or hint indexes, wallet sync state, pool membership state, or Data Layer root/store state with direct security impact
- Fast validation: force rollback around `chia/data_layer/data_layer_wallet.py:create_update_state_spend` and assert stale spend state is purged before replayed data is reconsidered
