# Q3678: delete_all_keys applies the wrong privilege boundary to a public route

## Question
Can an unprivileged attacker reach RPC route `delete_all_keys` and control public RPC or WebSocket command arguments that select protected actions so that `WalletRpcApi.delete_all_keys` in `chia/wallet/wallet_rpc_api.py` executes a path where reach a privileged path in `delete_all_keys` from a nominally unprivileged public route or command shape, violating the invariant that unprivileged callers must not reach privileged daemon, keychain, or wallet actions and leading to Bypass of wallet, daemon, keychain, RPC, pool, or Data Layer authorization that enables unauthorized signing, key use, coin control, payout redirection, singleton mutation, or protected state transitions?

## Target
- File/function: chia/wallet/wallet_rpc_api.py:947 `WalletRpcApi.delete_all_keys`
- Entrypoint: RPC route `delete_all_keys`
- Attacker controls: public RPC or WebSocket command arguments that select protected actions
- Exploit idea: reach a privileged path in `delete_all_keys` from a nominally unprivileged public route or command shape
- Invariant to test: unprivileged callers must not reach privileged daemon, keychain, or wallet actions
- Expected Immunefi impact: Bypass of wallet, daemon, keychain, RPC, pool, or Data Layer authorization that enables unauthorized signing, key use, coin control, payout redirection, singleton mutation, or protected state transitions
- Fast validation: invoke `chia/wallet/wallet_rpc_api.py:delete_all_keys` through its public command path with unprivileged inputs and assert privilege checks fail before state changes
