# Q151: stop reuses authorization context across unrelated requests

## Question
Can an unprivileged attacker reach daemon WebSocket command path reaching `stop` and control one request's authorization context plus a second request that reuses cached state so that `WebSocketServer.stop` in `chia/daemon/server.py` executes a path where make `stop` carry one request's authorization context into another request that should be isolated, violating the invariant that authorization context from one request must not be reused for another requester or target and leading to Bypass of wallet, daemon, keychain, RPC, pool, or Data Layer authorization that enables unauthorized signing, key use, coin control, payout redirection, singleton mutation, or protected state transitions?

## Target
- File/function: chia/daemon/server.py:260 `WebSocketServer.stop`
- Entrypoint: daemon WebSocket command path reaching `stop`
- Attacker controls: one request's authorization context plus a second request that reuses cached state
- Exploit idea: make `stop` carry one request's authorization context into another request that should be isolated
- Invariant to test: authorization context from one request must not be reused for another requester or target
- Expected Immunefi impact: Bypass of wallet, daemon, keychain, RPC, pool, or Data Layer authorization that enables unauthorized signing, key use, coin control, payout redirection, singleton mutation, or protected state transitions
- Fast validation: issue back-to-back public requests through `chia/daemon/server.py:stop` with different identities and assert auth state cannot bleed across them
