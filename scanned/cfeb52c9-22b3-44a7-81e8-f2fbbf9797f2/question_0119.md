# Q119: check_keys reuses authorization context across unrelated requests

## Question
Can an unprivileged attacker reach keychain command path reaching `check_keys` and control one request's authorization context plus a second request that reuses cached state so that `KeychainServer.check_keys` in `chia/daemon/keychain_server.py` executes a path where make `check_keys` carry one request's authorization context into another request that should be isolated, violating the invariant that authorization context from one request must not be reused for another requester or target and leading to Bypass of wallet, daemon, keychain, RPC, pool, or Data Layer authorization that enables unauthorized signing, key use, coin control, payout redirection, singleton mutation, or protected state transitions?

## Target
- File/function: chia/daemon/keychain_server.py:248 `KeychainServer.check_keys`
- Entrypoint: keychain command path reaching `check_keys`
- Attacker controls: one request's authorization context plus a second request that reuses cached state
- Exploit idea: make `check_keys` carry one request's authorization context into another request that should be isolated
- Invariant to test: authorization context from one request must not be reused for another requester or target
- Expected Immunefi impact: Bypass of wallet, daemon, keychain, RPC, pool, or Data Layer authorization that enables unauthorized signing, key use, coin control, payout redirection, singleton mutation, or protected state transitions
- Fast validation: issue back-to-back public requests through `chia/daemon/keychain_server.py:check_keys` with different identities and assert auth state cannot bleed across them
