# Q142: setup_process_global_state applies the wrong privilege boundary to a public route

## Question
Can an unprivileged attacker reach daemon WebSocket command path reaching `setup_process_global_state` and control public RPC or WebSocket command arguments that select protected actions so that `WebSocketServer.setup_process_global_state` in `chia/daemon/server.py` executes a path where reach a privileged path in `setup_process_global_state` from a nominally unprivileged public route or command shape, violating the invariant that unprivileged callers must not reach privileged daemon, keychain, or wallet actions and leading to Bypass of wallet, daemon, keychain, RPC, pool, or Data Layer authorization that enables unauthorized signing, key use, coin control, payout redirection, singleton mutation, or protected state transitions?

## Target
- File/function: chia/daemon/server.py:245 `WebSocketServer.setup_process_global_state`
- Entrypoint: daemon WebSocket command path reaching `setup_process_global_state`
- Attacker controls: public RPC or WebSocket command arguments that select protected actions
- Exploit idea: reach a privileged path in `setup_process_global_state` from a nominally unprivileged public route or command shape
- Invariant to test: unprivileged callers must not reach privileged daemon, keychain, or wallet actions
- Expected Immunefi impact: Bypass of wallet, daemon, keychain, RPC, pool, or Data Layer authorization that enables unauthorized signing, key use, coin control, payout redirection, singleton mutation, or protected state transitions
- Fast validation: invoke `chia/daemon/server.py:setup_process_global_state` through its public command path with unprivileged inputs and assert privilege checks fail before state changes
