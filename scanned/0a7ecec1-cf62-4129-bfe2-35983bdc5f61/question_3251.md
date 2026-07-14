# Q3251: apply_signatures reuses authorization context across unrelated requests

## Question
Can an unprivileged attacker reach wallet RPC or wallet sync flow reaching `apply_signatures` and control one request's authorization context plus a second request that reuses cached state so that `Wallet.apply_signatures` in `chia/wallet/wallet.py` executes a path where make `apply_signatures` carry one request's authorization context into another request that should be isolated, violating the invariant that authorization context from one request must not be reused for another requester or target and leading to Bypass of wallet, daemon, keychain, RPC, pool, or Data Layer authorization that enables unauthorized signing, key use, coin control, payout redirection, singleton mutation, or protected state transitions?

## Target
- File/function: chia/wallet/wallet.py:661 `Wallet.apply_signatures`
- Entrypoint: wallet RPC or wallet sync flow reaching `apply_signatures`
- Attacker controls: one request's authorization context plus a second request that reuses cached state
- Exploit idea: make `apply_signatures` carry one request's authorization context into another request that should be isolated
- Invariant to test: authorization context from one request must not be reused for another requester or target
- Expected Immunefi impact: Bypass of wallet, daemon, keychain, RPC, pool, or Data Layer authorization that enables unauthorized signing, key use, coin control, payout redirection, singleton mutation, or protected state transitions
- Fast validation: issue back-to-back public requests through `chia/wallet/wallet.py:apply_signatures` with different identities and assert auth state cannot bleed across them
