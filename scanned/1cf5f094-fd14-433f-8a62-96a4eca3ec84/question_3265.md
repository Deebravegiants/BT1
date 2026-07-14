# Q3265: new_valid_weight_proof persists attacker-shaped wallet state across rescan or resubscribe paths

## Question
Can an unprivileged attacker reach wallet RPC or wallet sync flow reaching `new_valid_weight_proof` and control rescan, resubscribe, and restored-wallet state after attacker-influenced prior updates so that `WalletBlockchain.new_valid_weight_proof` in `chia/wallet/wallet_blockchain.py` executes a path where make `new_valid_weight_proof` preserve attacker-shaped state even after the wallet rescans or rebuilds subscriptions, violating the invariant that wallet rescan and resubscribe paths must clear attacker-shaped stale state before rebuilding and leading to Corruption of coin records, lineage, puzzle ownership, offer/trade settlement state, mempool or hint indexes, wallet sync state, pool membership state, or Data Layer root/store state with direct security impact?

## Target
- File/function: chia/wallet/wallet_blockchain.py:81 `WalletBlockchain.new_valid_weight_proof`
- Entrypoint: wallet RPC or wallet sync flow reaching `new_valid_weight_proof`
- Attacker controls: rescan, resubscribe, and restored-wallet state after attacker-influenced prior updates
- Exploit idea: make `new_valid_weight_proof` preserve attacker-shaped state even after the wallet rescans or rebuilds subscriptions
- Invariant to test: wallet rescan and resubscribe paths must clear attacker-shaped stale state before rebuilding
- Expected Immunefi impact: Corruption of coin records, lineage, puzzle ownership, offer/trade settlement state, mempool or hint indexes, wallet sync state, pool membership state, or Data Layer root/store state with direct security impact
- Fast validation: rescan after attacker-shaped prior updates through `chia/wallet/wallet_blockchain.py:new_valid_weight_proof` and assert rebuilt state discards stale or poisoned records
