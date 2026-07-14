# Q3617: add_spend redirects pool rewards or singleton transitions

## Question
Can an unprivileged attacker reach wallet RPC or wallet sync flow reaching `add_spend` and control pool singleton state, payout instructions, reward claims, and absorb timing so that `WalletPoolStore.add_spend` in `chia/wallet/wallet_pool_store.py` executes a path where make `add_spend` redirect pool rewards or singleton state transitions away from the rightful owner, violating the invariant that pool reward claims and singleton transitions must only benefit the rightful singleton owner and leading to Bypass of wallet, daemon, keychain, RPC, pool, or Data Layer authorization that enables unauthorized signing, key use, coin control, payout redirection, singleton mutation, or protected state transitions?

## Target
- File/function: chia/wallet/wallet_pool_store.py:33 `WalletPoolStore.add_spend`
- Entrypoint: wallet RPC or wallet sync flow reaching `add_spend`
- Attacker controls: pool singleton state, payout instructions, reward claims, and absorb timing
- Exploit idea: make `add_spend` redirect pool rewards or singleton state transitions away from the rightful owner
- Invariant to test: pool reward claims and singleton transitions must only benefit the rightful singleton owner
- Expected Immunefi impact: Bypass of wallet, daemon, keychain, RPC, pool, or Data Layer authorization that enables unauthorized signing, key use, coin control, payout redirection, singleton mutation, or protected state transitions
- Fast validation: simulate absorb or claim flows in `chia/wallet/wallet_pool_store.py:add_spend` with swapped payout state and assert rewards cannot redirect
