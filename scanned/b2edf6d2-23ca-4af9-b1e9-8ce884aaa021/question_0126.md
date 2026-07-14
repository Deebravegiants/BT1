# Q126: delete_key_by_fingerprint applies the wrong privilege boundary to a public route

## Question
Can an unprivileged attacker reach keychain command path reaching `delete_key_by_fingerprint` and control public RPC or WebSocket command arguments that select protected actions so that `KeychainServer.delete_key_by_fingerprint` in `chia/daemon/keychain_server.py` executes a path where reach a privileged path in `delete_key_by_fingerprint` from a nominally unprivileged public route or command shape, violating the invariant that unprivileged callers must not reach privileged daemon, keychain, or wallet actions and leading to Bypass of wallet, daemon, keychain, RPC, pool, or Data Layer authorization that enables unauthorized signing, key use, coin control, payout redirection, singleton mutation, or protected state transitions?

## Target
- File/function: chia/daemon/keychain_server.py:272 `KeychainServer.delete_key_by_fingerprint`
- Entrypoint: keychain command path reaching `delete_key_by_fingerprint`
- Attacker controls: public RPC or WebSocket command arguments that select protected actions
- Exploit idea: reach a privileged path in `delete_key_by_fingerprint` from a nominally unprivileged public route or command shape
- Invariant to test: unprivileged callers must not reach privileged daemon, keychain, or wallet actions
- Expected Immunefi impact: Bypass of wallet, daemon, keychain, RPC, pool, or Data Layer authorization that enables unauthorized signing, key use, coin control, payout redirection, singleton mutation, or protected state transitions
- Fast validation: invoke `chia/daemon/keychain_server.py:delete_key_by_fingerprint` through its public command path with unprivileged inputs and assert privilege checks fail before state changes
