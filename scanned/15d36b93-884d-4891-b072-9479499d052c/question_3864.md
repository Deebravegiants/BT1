# Q3864: execute_signing_instructions applies the wrong privilege boundary to a public route

## Question
Can an unprivileged attacker reach RPC route `execute_signing_instructions` and control public RPC or WebSocket command arguments that select protected actions so that `WalletRpcApi.execute_signing_instructions` in `chia/wallet/wallet_rpc_api.py` executes a path where reach a privileged path in `execute_signing_instructions` from a nominally unprivileged public route or command shape, violating the invariant that unprivileged callers must not reach privileged daemon, keychain, or wallet actions and leading to Bypass of wallet, daemon, keychain, RPC, pool, or Data Layer authorization that enables unauthorized signing, key use, coin control, payout redirection, singleton mutation, or protected state transitions?

## Target
- File/function: chia/wallet/wallet_rpc_api.py:3739 `WalletRpcApi.execute_signing_instructions`
- Entrypoint: RPC route `execute_signing_instructions`
- Attacker controls: public RPC or WebSocket command arguments that select protected actions
- Exploit idea: reach a privileged path in `execute_signing_instructions` from a nominally unprivileged public route or command shape
- Invariant to test: unprivileged callers must not reach privileged daemon, keychain, or wallet actions
- Expected Immunefi impact: Bypass of wallet, daemon, keychain, RPC, pool, or Data Layer authorization that enables unauthorized signing, key use, coin control, payout redirection, singleton mutation, or protected state transitions
- Fast validation: invoke `chia/wallet/wallet_rpc_api.py:execute_signing_instructions` through its public command path with unprivileged inputs and assert privilege checks fail before state changes
