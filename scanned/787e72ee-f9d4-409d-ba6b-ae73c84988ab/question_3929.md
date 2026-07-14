# Q3929: set_sync_mode corrupts sync state under reordered peer updates

## Question
Can an unprivileged attacker reach wallet RPC or wallet sync flow reaching `set_sync_mode` and control reordered peer updates, stale heights, and inconsistent state snapshots so that `WalletStateManager.set_sync_mode` in `chia/wallet/wallet_state_manager.py` executes a path where feed `set_sync_mode` stale and fresh sync data in attacker-chosen order until the stored wallet or node view becomes non-canonical, violating the invariant that the canonical sync view must converge regardless of attacker-controlled delivery order among valid messages and leading to Corruption of coin records, lineage, puzzle ownership, offer/trade settlement state, mempool or hint indexes, wallet sync state, pool membership state, or Data Layer root/store state with direct security impact?

## Target
- File/function: chia/wallet/wallet_state_manager.py:776 `WalletStateManager.set_sync_mode`
- Entrypoint: wallet RPC or wallet sync flow reaching `set_sync_mode`
- Attacker controls: reordered peer updates, stale heights, and inconsistent state snapshots
- Exploit idea: feed `set_sync_mode` stale and fresh sync data in attacker-chosen order until the stored wallet or node view becomes non-canonical
- Invariant to test: the canonical sync view must converge regardless of attacker-controlled delivery order among valid messages
- Expected Immunefi impact: Corruption of coin records, lineage, puzzle ownership, offer/trade settlement state, mempool or hint indexes, wallet sync state, pool membership state, or Data Layer root/store state with direct security impact
- Fast validation: reorder valid sync messages into `chia/wallet/wallet_state_manager.py:set_sync_mode` and assert the final stored state matches canonical chain order
