# Q689: remove_mempool_item redirects pool rewards or singleton transitions

## Question
Can an unprivileged attacker reach full node mempool, sync, or peer flow reaching `remove_mempool_item` and control pool singleton state, payout instructions, reward claims, and absorb timing so that `BitcoinFeeEstimator.remove_mempool_item` in `chia/full_node/bitcoin_fee_estimator.py` executes a path where make `remove_mempool_item` redirect pool rewards or singleton state transitions away from the rightful owner, violating the invariant that pool reward claims and singleton transitions must only benefit the rightful singleton owner and leading to Bypass of wallet, daemon, keychain, RPC, pool, or Data Layer authorization that enables unauthorized signing, key use, coin control, payout redirection, singleton mutation, or protected state transitions?

## Target
- File/function: chia/full_node/bitcoin_fee_estimator.py:42 `BitcoinFeeEstimator.remove_mempool_item`
- Entrypoint: full node mempool, sync, or peer flow reaching `remove_mempool_item`
- Attacker controls: pool singleton state, payout instructions, reward claims, and absorb timing
- Exploit idea: make `remove_mempool_item` redirect pool rewards or singleton state transitions away from the rightful owner
- Invariant to test: pool reward claims and singleton transitions must only benefit the rightful singleton owner
- Expected Immunefi impact: Bypass of wallet, daemon, keychain, RPC, pool, or Data Layer authorization that enables unauthorized signing, key use, coin control, payout redirection, singleton mutation, or protected state transitions
- Fast validation: simulate absorb or claim flows in `chia/full_node/bitcoin_fee_estimator.py:remove_mempool_item` with swapped payout state and assert rewards cannot redirect
