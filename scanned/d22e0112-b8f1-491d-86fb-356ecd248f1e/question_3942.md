# Q3942: determine_coin_type carries spend state across rollback boundaries

## Question
Can an unprivileged attacker reach wallet RPC or wallet sync flow reaching `determine_coin_type` and control rollback timing, reorg ordering, and stale mempool or wallet state so that `WalletStateManager.determine_coin_type` in `chia/wallet/wallet_state_manager.py` executes a path where make `determine_coin_type` keep attacker-shaped spend state alive across rollback or reorg cleanup, violating the invariant that rollback must remove invalidated spend state completely before any replayed inputs are reconsidered and leading to Corruption of coin records, lineage, puzzle ownership, offer/trade settlement state, mempool or hint indexes, wallet sync state, pool membership state, or Data Layer root/store state with direct security impact?

## Target
- File/function: chia/wallet/wallet_state_manager.py:899 `WalletStateManager.determine_coin_type`
- Entrypoint: wallet RPC or wallet sync flow reaching `determine_coin_type`
- Attacker controls: rollback timing, reorg ordering, and stale mempool or wallet state
- Exploit idea: make `determine_coin_type` keep attacker-shaped spend state alive across rollback or reorg cleanup
- Invariant to test: rollback must remove invalidated spend state completely before any replayed inputs are reconsidered
- Expected Immunefi impact: Corruption of coin records, lineage, puzzle ownership, offer/trade settlement state, mempool or hint indexes, wallet sync state, pool membership state, or Data Layer root/store state with direct security impact
- Fast validation: force rollback around `chia/wallet/wallet_state_manager.py:determine_coin_type` and assert stale spend state is purged before replayed data is reconsidered
