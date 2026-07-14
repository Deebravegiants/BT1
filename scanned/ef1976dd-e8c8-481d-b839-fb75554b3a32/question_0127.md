# Q127: delete_key_by_fingerprint reuses authorization context across unrelated requests

## Question
Can an unprivileged attacker reach keychain command path reaching `delete_key_by_fingerprint` and control one request's authorization context plus a second request that reuses cached state so that `KeychainServer.delete_key_by_fingerprint` in `chia/daemon/keychain_server.py` executes a path where make `delete_key_by_fingerprint` carry one request's authorization context into another request that should be isolated, violating the invariant that authorization context from one request must not be reused for another requester or target and leading to Bypass of wallet, daemon, keychain, RPC, pool, or Data Layer authorization that enables unauthorized signing, key use, coin control, payout redirection, singleton mutation, or protected state transitions?

## Target
- File/function: chia/daemon/keychain_server.py:272 `KeychainServer.delete_key_by_fingerprint`
- Entrypoint: keychain command path reaching `delete_key_by_fingerprint`
- Attacker controls: one request's authorization context plus a second request that reuses cached state
- Exploit idea: make `delete_key_by_fingerprint` carry one request's authorization context into another request that should be isolated
- Invariant to test: authorization context from one request must not be reused for another requester or target
- Expected Immunefi impact: Bypass of wallet, daemon, keychain, RPC, pool, or Data Layer authorization that enables unauthorized signing, key use, coin control, payout redirection, singleton mutation, or protected state transitions
- Fast validation: issue back-to-back public requests through `chia/daemon/keychain_server.py:delete_key_by_fingerprint` with different identities and assert auth state cannot bleed across them
