# Q1869: generate_signed_transaction reuses authorization context across unrelated requests

## Question
Can an unprivileged attacker reach pool wallet or singleton spend flow reaching `generate_signed_transaction` and control one request's authorization context plus a second request that reuses cached state so that `PoolWallet.generate_signed_transaction` in `chia/pools/pool_wallet.py` executes a path where make `generate_signed_transaction` carry one request's authorization context into another request that should be isolated, violating the invariant that authorization context from one request must not be reused for another requester or target and leading to Bypass of wallet, daemon, keychain, RPC, pool, or Data Layer authorization that enables unauthorized signing, key use, coin control, payout redirection, singleton mutation, or protected state transitions?

## Target
- File/function: chia/pools/pool_wallet.py:899 `PoolWallet.generate_signed_transaction`
- Entrypoint: pool wallet or singleton spend flow reaching `generate_signed_transaction`
- Attacker controls: one request's authorization context plus a second request that reuses cached state
- Exploit idea: make `generate_signed_transaction` carry one request's authorization context into another request that should be isolated
- Invariant to test: authorization context from one request must not be reused for another requester or target
- Expected Immunefi impact: Bypass of wallet, daemon, keychain, RPC, pool, or Data Layer authorization that enables unauthorized signing, key use, coin control, payout redirection, singleton mutation, or protected state transitions
- Fast validation: issue back-to-back public requests through `chia/pools/pool_wallet.py:generate_signed_transaction` with different identities and assert auth state cannot bleed across them
