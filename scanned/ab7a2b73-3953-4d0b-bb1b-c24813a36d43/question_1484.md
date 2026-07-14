# Q1484: add_spend_bundle redirects pool rewards or singleton transitions

## Question
Can an unprivileged attacker reach full node mempool, sync, or peer flow reaching `add_spend_bundle` and control pool singleton state, payout instructions, reward claims, and absorb timing so that `MempoolManager.add_spend_bundle` in `chia/full_node/mempool_manager.py` executes a path where make `add_spend_bundle` redirect pool rewards or singleton state transitions away from the rightful owner, violating the invariant that pool reward claims and singleton transitions must only benefit the rightful singleton owner and leading to Bypass of wallet, daemon, keychain, RPC, pool, or Data Layer authorization that enables unauthorized signing, key use, coin control, payout redirection, singleton mutation, or protected state transitions?

## Target
- File/function: chia/full_node/mempool_manager.py:552 `MempoolManager.add_spend_bundle`
- Entrypoint: full node mempool, sync, or peer flow reaching `add_spend_bundle`
- Attacker controls: pool singleton state, payout instructions, reward claims, and absorb timing
- Exploit idea: make `add_spend_bundle` redirect pool rewards or singleton state transitions away from the rightful owner
- Invariant to test: pool reward claims and singleton transitions must only benefit the rightful singleton owner
- Expected Immunefi impact: Bypass of wallet, daemon, keychain, RPC, pool, or Data Layer authorization that enables unauthorized signing, key use, coin control, payout redirection, singleton mutation, or protected state transitions
- Fast validation: simulate absorb or claim flows in `chia/full_node/mempool_manager.py:add_spend_bundle` with swapped payout state and assert rewards cannot redirect
