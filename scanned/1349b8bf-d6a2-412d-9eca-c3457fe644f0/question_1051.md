# Q1051: request_mempool_transactions redirects pool rewards or singleton transitions

## Question
Can an unprivileged attacker reach P2P message handler `request_mempool_transactions` and control pool singleton state, payout instructions, reward claims, and absorb timing so that `FullNodeAPI.request_mempool_transactions` in `chia/full_node/full_node_api.py` executes a path where make `request_mempool_transactions` redirect pool rewards or singleton state transitions away from the rightful owner, violating the invariant that pool reward claims and singleton transitions must only benefit the rightful singleton owner and leading to Bypass of wallet, daemon, keychain, RPC, pool, or Data Layer authorization that enables unauthorized signing, key use, coin control, payout redirection, singleton mutation, or protected state transitions?

## Target
- File/function: chia/full_node/full_node_api.py:875 `FullNodeAPI.request_mempool_transactions`
- Entrypoint: P2P message handler `request_mempool_transactions`
- Attacker controls: pool singleton state, payout instructions, reward claims, and absorb timing
- Exploit idea: make `request_mempool_transactions` redirect pool rewards or singleton state transitions away from the rightful owner
- Invariant to test: pool reward claims and singleton transitions must only benefit the rightful singleton owner
- Expected Immunefi impact: Bypass of wallet, daemon, keychain, RPC, pool, or Data Layer authorization that enables unauthorized signing, key use, coin control, payout redirection, singleton mutation, or protected state transitions
- Fast validation: simulate absorb or claim flows in `chia/full_node/full_node_api.py:request_mempool_transactions` with swapped payout state and assert rewards cannot redirect
