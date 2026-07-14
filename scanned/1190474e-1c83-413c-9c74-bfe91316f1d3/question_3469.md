# Q3469: sync_from_untrusted_close_to_peak corrupts sync state under reordered peer updates

## Question
Can an unprivileged attacker reach wallet RPC or wallet sync flow reaching `sync_from_untrusted_close_to_peak` and control reordered peer updates, stale heights, and inconsistent state snapshots so that `WalletNode.sync_from_untrusted_close_to_peak` in `chia/wallet/wallet_node.py` executes a path where feed `sync_from_untrusted_close_to_peak` stale and fresh sync data in attacker-chosen order until the stored wallet or node view becomes non-canonical, violating the invariant that the canonical sync view must converge regardless of attacker-controlled delivery order among valid messages and leading to Corruption of coin records, lineage, puzzle ownership, offer/trade settlement state, mempool or hint indexes, wallet sync state, pool membership state, or Data Layer root/store state with direct security impact?

## Target
- File/function: chia/wallet/wallet_node.py:1339 `WalletNode.sync_from_untrusted_close_to_peak`
- Entrypoint: wallet RPC or wallet sync flow reaching `sync_from_untrusted_close_to_peak`
- Attacker controls: reordered peer updates, stale heights, and inconsistent state snapshots
- Exploit idea: feed `sync_from_untrusted_close_to_peak` stale and fresh sync data in attacker-chosen order until the stored wallet or node view becomes non-canonical
- Invariant to test: the canonical sync view must converge regardless of attacker-controlled delivery order among valid messages
- Expected Immunefi impact: Corruption of coin records, lineage, puzzle ownership, offer/trade settlement state, mempool or hint indexes, wallet sync state, pool membership state, or Data Layer root/store state with direct security impact
- Fast validation: reorder valid sync messages into `chia/wallet/wallet_node.py:sync_from_untrusted_close_to_peak` and assert the final stored state matches canonical chain order
