# Q175: remove_keyring_passphrase reuses authorization context across unrelated requests

## Question
Can an unprivileged attacker reach daemon WebSocket command path reaching `remove_keyring_passphrase` and control one request's authorization context plus a second request that reuses cached state so that `WebSocketServer.remove_keyring_passphrase` in `chia/daemon/server.py` executes a path where make `remove_keyring_passphrase` carry one request's authorization context into another request that should be isolated, violating the invariant that authorization context from one request must not be reused for another requester or target and leading to Bypass of wallet, daemon, keychain, RPC, pool, or Data Layer authorization that enables unauthorized signing, key use, coin control, payout redirection, singleton mutation, or protected state transitions?

## Target
- File/function: chia/daemon/server.py:616 `WebSocketServer.remove_keyring_passphrase`
- Entrypoint: daemon WebSocket command path reaching `remove_keyring_passphrase`
- Attacker controls: one request's authorization context plus a second request that reuses cached state
- Exploit idea: make `remove_keyring_passphrase` carry one request's authorization context into another request that should be isolated
- Invariant to test: authorization context from one request must not be reused for another requester or target
- Expected Immunefi impact: Bypass of wallet, daemon, keychain, RPC, pool, or Data Layer authorization that enables unauthorized signing, key use, coin control, payout redirection, singleton mutation, or protected state transitions
- Fast validation: issue back-to-back public requests through `chia/daemon/server.py:remove_keyring_passphrase` with different identities and assert auth state cannot bleed across them
