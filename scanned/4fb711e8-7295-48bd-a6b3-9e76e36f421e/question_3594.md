# Q3594: respond_ses_hashes persists attacker-shaped wallet state across rescan or resubscribe paths

## Question
Can an unprivileged attacker reach P2P message handler `respond_ses_hashes` and control rescan, resubscribe, and restored-wallet state after attacker-influenced prior updates so that `WalletNodeAPI.respond_ses_hashes` in `chia/wallet/wallet_node_api.py` executes a path where make `respond_ses_hashes` preserve attacker-shaped state even after the wallet rescans or rebuilds subscriptions, violating the invariant that wallet rescan and resubscribe paths must clear attacker-shaped stale state before rebuilding and leading to Corruption of coin records, lineage, puzzle ownership, offer/trade settlement state, mempool or hint indexes, wallet sync state, pool membership state, or Data Layer root/store state with direct security impact?

## Target
- File/function: chia/wallet/wallet_node_api.py:212 `WalletNodeAPI.respond_ses_hashes`
- Entrypoint: P2P message handler `respond_ses_hashes`
- Attacker controls: rescan, resubscribe, and restored-wallet state after attacker-influenced prior updates
- Exploit idea: make `respond_ses_hashes` preserve attacker-shaped state even after the wallet rescans or rebuilds subscriptions
- Invariant to test: wallet rescan and resubscribe paths must clear attacker-shaped stale state before rebuilding
- Expected Immunefi impact: Corruption of coin records, lineage, puzzle ownership, offer/trade settlement state, mempool or hint indexes, wallet sync state, pool membership state, or Data Layer root/store state with direct security impact
- Fast validation: rescan after attacker-shaped prior updates through `chia/wallet/wallet_node_api.py:respond_ses_hashes` and assert rebuilt state discards stale or poisoned records
