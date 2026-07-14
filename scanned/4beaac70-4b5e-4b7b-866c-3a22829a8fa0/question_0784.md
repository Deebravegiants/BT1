# Q784: new_mempool_tx redirects pool rewards or singleton transitions

## Question
Can an unprivileged attacker reach full node mempool, sync, or peer flow reaching `new_mempool_tx` and control pool singleton state, payout instructions, reward claims, and absorb timing so that `FeeStat.new_mempool_tx` in `chia/full_node/fee_tracker.py` executes a path where make `new_mempool_tx` redirect pool rewards or singleton state transitions away from the rightful owner, violating the invariant that pool reward claims and singleton transitions must only benefit the rightful singleton owner and leading to Bypass of wallet, daemon, keychain, RPC, pool, or Data Layer authorization that enables unauthorized signing, key use, coin control, payout redirection, singleton mutation, or protected state transitions?

## Target
- File/function: chia/full_node/fee_tracker.py:162 `FeeStat.new_mempool_tx`
- Entrypoint: full node mempool, sync, or peer flow reaching `new_mempool_tx`
- Attacker controls: pool singleton state, payout instructions, reward claims, and absorb timing
- Exploit idea: make `new_mempool_tx` redirect pool rewards or singleton state transitions away from the rightful owner
- Invariant to test: pool reward claims and singleton transitions must only benefit the rightful singleton owner
- Expected Immunefi impact: Bypass of wallet, daemon, keychain, RPC, pool, or Data Layer authorization that enables unauthorized signing, key use, coin control, payout redirection, singleton mutation, or protected state transitions
- Fast validation: simulate absorb or claim flows in `chia/full_node/fee_tracker.py:new_mempool_tx` with swapped payout state and assert rewards cannot redirect
