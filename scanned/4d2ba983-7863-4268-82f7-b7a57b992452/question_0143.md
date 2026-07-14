# Q143: setup_process_global_state reuses authorization context across unrelated requests

## Question
Can an unprivileged attacker reach daemon WebSocket command path reaching `setup_process_global_state` and control one request's authorization context plus a second request that reuses cached state so that `WebSocketServer.setup_process_global_state` in `chia/daemon/server.py` executes a path where make `setup_process_global_state` carry one request's authorization context into another request that should be isolated, violating the invariant that authorization context from one request must not be reused for another requester or target and leading to Bypass of wallet, daemon, keychain, RPC, pool, or Data Layer authorization that enables unauthorized signing, key use, coin control, payout redirection, singleton mutation, or protected state transitions?

## Target
- File/function: chia/daemon/server.py:245 `WebSocketServer.setup_process_global_state`
- Entrypoint: daemon WebSocket command path reaching `setup_process_global_state`
- Attacker controls: one request's authorization context plus a second request that reuses cached state
- Exploit idea: make `setup_process_global_state` carry one request's authorization context into another request that should be isolated
- Invariant to test: authorization context from one request must not be reused for another requester or target
- Expected Immunefi impact: Bypass of wallet, daemon, keychain, RPC, pool, or Data Layer authorization that enables unauthorized signing, key use, coin control, payout redirection, singleton mutation, or protected state transitions
- Fast validation: issue back-to-back public requests through `chia/daemon/server.py:setup_process_global_state` with different identities and assert auth state cannot bleed across them
