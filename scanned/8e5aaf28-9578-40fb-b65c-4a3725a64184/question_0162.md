# Q162: unlock_keyring applies the wrong privilege boundary to a public route

## Question
Can an unprivileged attacker reach daemon WebSocket command path reaching `unlock_keyring` and control public RPC or WebSocket command arguments that select protected actions so that `WebSocketServer.unlock_keyring` in `chia/daemon/server.py` executes a path where reach a privileged path in `unlock_keyring` from a nominally unprivileged public route or command shape, violating the invariant that unprivileged callers must not reach privileged daemon, keychain, or wallet actions and leading to Bypass of wallet, daemon, keychain, RPC, pool, or Data Layer authorization that enables unauthorized signing, key use, coin control, payout redirection, singleton mutation, or protected state transitions?

## Target
- File/function: chia/daemon/server.py:519 `WebSocketServer.unlock_keyring`
- Entrypoint: daemon WebSocket command path reaching `unlock_keyring`
- Attacker controls: public RPC or WebSocket command arguments that select protected actions
- Exploit idea: reach a privileged path in `unlock_keyring` from a nominally unprivileged public route or command shape
- Invariant to test: unprivileged callers must not reach privileged daemon, keychain, or wallet actions
- Expected Immunefi impact: Bypass of wallet, daemon, keychain, RPC, pool, or Data Layer authorization that enables unauthorized signing, key use, coin control, payout redirection, singleton mutation, or protected state transitions
- Fast validation: invoke `chia/daemon/server.py:unlock_keyring` through its public command path with unprivileged inputs and assert privilege checks fail before state changes
