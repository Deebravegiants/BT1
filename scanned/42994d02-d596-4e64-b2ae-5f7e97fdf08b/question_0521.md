# Q521: add_key_value applies the wrong privilege boundary to a public route

## Question
Can an unprivileged attacker reach Data Layer wallet, sync, or store flow reaching `add_key_value` and control public RPC or WebSocket command arguments that select protected actions so that `DataStore.add_key_value` in `chia/data_layer/data_store.py` executes a path where reach a privileged path in `add_key_value` from a nominally unprivileged public route or command shape, violating the invariant that unprivileged callers must not reach privileged daemon, keychain, or wallet actions and leading to Bypass of wallet, daemon, keychain, RPC, pool, or Data Layer authorization that enables unauthorized signing, key use, coin control, payout redirection, singleton mutation, or protected state transitions?

## Target
- File/function: chia/data_layer/data_store.py:710 `DataStore.add_key_value`
- Entrypoint: Data Layer wallet, sync, or store flow reaching `add_key_value`
- Attacker controls: public RPC or WebSocket command arguments that select protected actions
- Exploit idea: reach a privileged path in `add_key_value` from a nominally unprivileged public route or command shape
- Invariant to test: unprivileged callers must not reach privileged daemon, keychain, or wallet actions
- Expected Immunefi impact: Bypass of wallet, daemon, keychain, RPC, pool, or Data Layer authorization that enables unauthorized signing, key use, coin control, payout redirection, singleton mutation, or protected state transitions
- Fast validation: invoke `chia/data_layer/data_store.py:add_key_value` through its public command path with unprivileged inputs and assert privilege checks fail before state changes
