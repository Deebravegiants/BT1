# Q3978: handle_cat persists attacker-shaped wallet state across rescan or resubscribe paths

## Question
Can an unprivileged attacker reach wallet RPC or wallet sync flow reaching `handle_cat` and control rescan, resubscribe, and restored-wallet state after attacker-influenced prior updates so that `WalletStateManager.handle_cat` in `chia/wallet/wallet_state_manager.py` executes a path where make `handle_cat` preserve attacker-shaped state even after the wallet rescans or rebuilds subscriptions, violating the invariant that wallet rescan and resubscribe paths must clear attacker-shaped stale state before rebuilding and leading to Corruption of coin records, lineage, puzzle ownership, offer/trade settlement state, mempool or hint indexes, wallet sync state, pool membership state, or Data Layer root/store state with direct security impact?

## Target
- File/function: chia/wallet/wallet_state_manager.py:1228 `WalletStateManager.handle_cat`
- Entrypoint: wallet RPC or wallet sync flow reaching `handle_cat`
- Attacker controls: rescan, resubscribe, and restored-wallet state after attacker-influenced prior updates
- Exploit idea: make `handle_cat` preserve attacker-shaped state even after the wallet rescans or rebuilds subscriptions
- Invariant to test: wallet rescan and resubscribe paths must clear attacker-shaped stale state before rebuilding
- Expected Immunefi impact: Corruption of coin records, lineage, puzzle ownership, offer/trade settlement state, mempool or hint indexes, wallet sync state, pool membership state, or Data Layer root/store state with direct security impact
- Fast validation: rescan after attacker-shaped prior updates through `chia/wallet/wallet_state_manager.py:handle_cat` and assert rebuilt state discards stale or poisoned records
