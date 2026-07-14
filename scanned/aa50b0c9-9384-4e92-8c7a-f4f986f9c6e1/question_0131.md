# Q131: get_all_private_keys reuses authorization context across unrelated requests

## Question
Can an unprivileged attacker reach keychain command path reaching `get_all_private_keys` and control one request's authorization context plus a second request that reuses cached state so that `KeychainServer.get_all_private_keys` in `chia/daemon/keychain_server.py` executes a path where make `get_all_private_keys` carry one request's authorization context into another request that should be isolated, violating the invariant that authorization context from one request must not be reused for another requester or target and leading to Bypass of wallet, daemon, keychain, RPC, pool, or Data Layer authorization that enables unauthorized signing, key use, coin control, payout redirection, singleton mutation, or protected state transitions?

## Target
- File/function: chia/daemon/keychain_server.py:317 `KeychainServer.get_all_private_keys`
- Entrypoint: keychain command path reaching `get_all_private_keys`
- Attacker controls: one request's authorization context plus a second request that reuses cached state
- Exploit idea: make `get_all_private_keys` carry one request's authorization context into another request that should be isolated
- Invariant to test: authorization context from one request must not be reused for another requester or target
- Expected Immunefi impact: Bypass of wallet, daemon, keychain, RPC, pool, or Data Layer authorization that enables unauthorized signing, key use, coin control, payout redirection, singleton mutation, or protected state transitions
- Fast validation: issue back-to-back public requests through `chia/daemon/keychain_server.py:get_all_private_keys` with different identities and assert auth state cannot bleed across them
