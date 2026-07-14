# Q1411: update_spend_index redirects pool rewards or singleton transitions

## Question
Can an unprivileged attacker reach full node mempool, sync, or peer flow reaching `update_spend_index` and control pool singleton state, payout instructions, reward claims, and absorb timing so that `Mempool.update_spend_index` in `chia/full_node/mempool.py` executes a path where make `update_spend_index` redirect pool rewards or singleton state transitions away from the rightful owner, violating the invariant that pool reward claims and singleton transitions must only benefit the rightful singleton owner and leading to Bypass of wallet, daemon, keychain, RPC, pool, or Data Layer authorization that enables unauthorized signing, key use, coin control, payout redirection, singleton mutation, or protected state transitions?

## Target
- File/function: chia/full_node/mempool.py:505 `Mempool.update_spend_index`
- Entrypoint: full node mempool, sync, or peer flow reaching `update_spend_index`
- Attacker controls: pool singleton state, payout instructions, reward claims, and absorb timing
- Exploit idea: make `update_spend_index` redirect pool rewards or singleton state transitions away from the rightful owner
- Invariant to test: pool reward claims and singleton transitions must only benefit the rightful singleton owner
- Expected Immunefi impact: Bypass of wallet, daemon, keychain, RPC, pool, or Data Layer authorization that enables unauthorized signing, key use, coin control, payout redirection, singleton mutation, or protected state transitions
- Fast validation: simulate absorb or claim flows in `chia/full_node/mempool.py:update_spend_index` with swapped payout state and assert rewards cannot redirect
