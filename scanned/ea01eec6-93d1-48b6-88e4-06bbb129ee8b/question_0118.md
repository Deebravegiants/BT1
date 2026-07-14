# Q118: check_keys applies the wrong privilege boundary to a public route

## Question
Can an unprivileged attacker reach keychain command path reaching `check_keys` and control public RPC or WebSocket command arguments that select protected actions so that `KeychainServer.check_keys` in `chia/daemon/keychain_server.py` executes a path where reach a privileged path in `check_keys` from a nominally unprivileged public route or command shape, violating the invariant that unprivileged callers must not reach privileged daemon, keychain, or wallet actions and leading to Bypass of wallet, daemon, keychain, RPC, pool, or Data Layer authorization that enables unauthorized signing, key use, coin control, payout redirection, singleton mutation, or protected state transitions?

## Target
- File/function: chia/daemon/keychain_server.py:248 `KeychainServer.check_keys`
- Entrypoint: keychain command path reaching `check_keys`
- Attacker controls: public RPC or WebSocket command arguments that select protected actions
- Exploit idea: reach a privileged path in `check_keys` from a nominally unprivileged public route or command shape
- Invariant to test: unprivileged callers must not reach privileged daemon, keychain, or wallet actions
- Expected Immunefi impact: Bypass of wallet, daemon, keychain, RPC, pool, or Data Layer authorization that enables unauthorized signing, key use, coin control, payout redirection, singleton mutation, or protected state transitions
- Fast validation: invoke `chia/daemon/keychain_server.py:check_keys` through its public command path with unprivileged inputs and assert privilege checks fail before state changes
