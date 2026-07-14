# Q1821: claim_pool_rewards redirects pool rewards or singleton transitions

## Question
Can an unprivileged attacker reach pool wallet or singleton spend flow reaching `claim_pool_rewards` and control pool singleton state, payout instructions, reward claims, and absorb timing so that `PoolWallet.claim_pool_rewards` in `chia/pools/pool_wallet.py` executes a path where make `claim_pool_rewards` redirect pool rewards or singleton state transitions away from the rightful owner, violating the invariant that pool reward claims and singleton transitions must only benefit the rightful singleton owner and leading to Bypass of wallet, daemon, keychain, RPC, pool, or Data Layer authorization that enables unauthorized signing, key use, coin control, payout redirection, singleton mutation, or protected state transitions?

## Target
- File/function: chia/pools/pool_wallet.py:712 `PoolWallet.claim_pool_rewards`
- Entrypoint: pool wallet or singleton spend flow reaching `claim_pool_rewards`
- Attacker controls: pool singleton state, payout instructions, reward claims, and absorb timing
- Exploit idea: make `claim_pool_rewards` redirect pool rewards or singleton state transitions away from the rightful owner
- Invariant to test: pool reward claims and singleton transitions must only benefit the rightful singleton owner
- Expected Immunefi impact: Bypass of wallet, daemon, keychain, RPC, pool, or Data Layer authorization that enables unauthorized signing, key use, coin control, payout redirection, singleton mutation, or protected state transitions
- Fast validation: simulate absorb or claim flows in `chia/pools/pool_wallet.py:claim_pool_rewards` with swapped payout state and assert rewards cannot redirect
