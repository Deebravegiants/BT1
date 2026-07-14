# Q1813: generate_launcher_spend redirects pool rewards or singleton transitions

## Question
Can an unprivileged attacker reach pool wallet or singleton spend flow reaching `generate_launcher_spend` and control pool singleton state, payout instructions, reward claims, and absorb timing so that `PoolWallet.generate_launcher_spend` in `chia/pools/pool_wallet.py` executes a path where make `generate_launcher_spend` redirect pool rewards or singleton state transitions away from the rightful owner, violating the invariant that pool reward claims and singleton transitions must only benefit the rightful singleton owner and leading to Bypass of wallet, daemon, keychain, RPC, pool, or Data Layer authorization that enables unauthorized signing, key use, coin control, payout redirection, singleton mutation, or protected state transitions?

## Target
- File/function: chia/pools/pool_wallet.py:545 `PoolWallet.generate_launcher_spend`
- Entrypoint: pool wallet or singleton spend flow reaching `generate_launcher_spend`
- Attacker controls: pool singleton state, payout instructions, reward claims, and absorb timing
- Exploit idea: make `generate_launcher_spend` redirect pool rewards or singleton state transitions away from the rightful owner
- Invariant to test: pool reward claims and singleton transitions must only benefit the rightful singleton owner
- Expected Immunefi impact: Bypass of wallet, daemon, keychain, RPC, pool, or Data Layer authorization that enables unauthorized signing, key use, coin control, payout redirection, singleton mutation, or protected state transitions
- Fast validation: simulate absorb or claim flows in `chia/pools/pool_wallet.py:generate_launcher_spend` with swapped payout state and assert rewards cannot redirect
