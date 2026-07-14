# Q3501: new_peak_wallet persists attacker-shaped wallet state across rescan or resubscribe paths

## Question
Can an unprivileged attacker reach P2P message handler `new_peak_wallet` and control rescan, resubscribe, and restored-wallet state after attacker-influenced prior updates so that `WalletNodeAPI.new_peak_wallet` in `chia/wallet/wallet_node_api.py` executes a path where make `new_peak_wallet` preserve attacker-shaped state even after the wallet rescans or rebuilds subscriptions, violating the invariant that wallet rescan and resubscribe paths must clear attacker-shaped stale state before rebuilding and leading to Corruption of coin records, lineage, puzzle ownership, offer/trade settlement state, mempool or hint indexes, wallet sync state, pool membership state, or Data Layer root/store state with direct security impact?

## Target
- File/function: chia/wallet/wallet_node_api.py:53 `WalletNodeAPI.new_peak_wallet`
- Entrypoint: P2P message handler `new_peak_wallet`
- Attacker controls: rescan, resubscribe, and restored-wallet state after attacker-influenced prior updates
- Exploit idea: make `new_peak_wallet` preserve attacker-shaped state even after the wallet rescans or rebuilds subscriptions
- Invariant to test: wallet rescan and resubscribe paths must clear attacker-shaped stale state before rebuilding
- Expected Immunefi impact: Corruption of coin records, lineage, puzzle ownership, offer/trade settlement state, mempool or hint indexes, wallet sync state, pool membership state, or Data Layer root/store state with direct security impact
- Fast validation: rescan after attacker-shaped prior updates through `chia/wallet/wallet_node_api.py:new_peak_wallet` and assert rebuilt state discards stale or poisoned records
