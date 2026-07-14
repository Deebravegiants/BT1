# Q3292: set_finished_sync_up_to persists attacker-shaped wallet state across rescan or resubscribe paths

## Question
Can an unprivileged attacker reach wallet RPC or wallet sync flow reaching `set_finished_sync_up_to` and control rescan, resubscribe, and restored-wallet state after attacker-influenced prior updates so that `WalletBlockchain.set_finished_sync_up_to` in `chia/wallet/wallet_blockchain.py` executes a path where make `set_finished_sync_up_to` preserve attacker-shaped state even after the wallet rescans or rebuilds subscriptions, violating the invariant that wallet rescan and resubscribe paths must clear attacker-shaped stale state before rebuilding and leading to Corruption of coin records, lineage, puzzle ownership, offer/trade settlement state, mempool or hint indexes, wallet sync state, pool membership state, or Data Layer root/store state with direct security impact?

## Target
- File/function: chia/wallet/wallet_blockchain.py:197 `WalletBlockchain.set_finished_sync_up_to`
- Entrypoint: wallet RPC or wallet sync flow reaching `set_finished_sync_up_to`
- Attacker controls: rescan, resubscribe, and restored-wallet state after attacker-influenced prior updates
- Exploit idea: make `set_finished_sync_up_to` preserve attacker-shaped state even after the wallet rescans or rebuilds subscriptions
- Invariant to test: wallet rescan and resubscribe paths must clear attacker-shaped stale state before rebuilding
- Expected Immunefi impact: Corruption of coin records, lineage, puzzle ownership, offer/trade settlement state, mempool or hint indexes, wallet sync state, pool membership state, or Data Layer root/store state with direct security impact
- Fast validation: rescan after attacker-shaped prior updates through `chia/wallet/wallet_blockchain.py:set_finished_sync_up_to` and assert rebuilt state discards stale or poisoned records
