# Q178: start_plotting applies the wrong privilege boundary to a public route

## Question
Can an unprivileged attacker reach daemon WebSocket command path reaching `start_plotting` and control public RPC or WebSocket command arguments that select protected actions so that `WebSocketServer.start_plotting` in `chia/daemon/server.py` executes a path where reach a privileged path in `start_plotting` from a nominally unprivileged public route or command shape, violating the invariant that unprivileged callers must not reach privileged daemon, keychain, or wallet actions and leading to Bypass of wallet, daemon, keychain, RPC, pool, or Data Layer authorization that enables unauthorized signing, key use, coin control, payout redirection, singleton mutation, or protected state transitions?

## Target
- File/function: chia/daemon/server.py:1158 `WebSocketServer.start_plotting`
- Entrypoint: daemon WebSocket command path reaching `start_plotting`
- Attacker controls: public RPC or WebSocket command arguments that select protected actions
- Exploit idea: reach a privileged path in `start_plotting` from a nominally unprivileged public route or command shape
- Invariant to test: unprivileged callers must not reach privileged daemon, keychain, or wallet actions
- Expected Immunefi impact: Bypass of wallet, daemon, keychain, RPC, pool, or Data Layer authorization that enables unauthorized signing, key use, coin control, payout redirection, singleton mutation, or protected state transitions
- Fast validation: invoke `chia/daemon/server.py:start_plotting` through its public command path with unprivileged inputs and assert privilege checks fail before state changes
