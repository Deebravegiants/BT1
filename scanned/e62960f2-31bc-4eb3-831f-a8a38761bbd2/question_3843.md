# Q3843: create_signed_transaction applies the wrong privilege boundary to a public route

## Question
Can an unprivileged attacker reach RPC route `create_signed_transaction` and control public RPC or WebSocket command arguments that select protected actions so that `WalletRpcApi.create_signed_transaction` in `chia/wallet/wallet_rpc_api.py` executes a path where reach a privileged path in `create_signed_transaction` from a nominally unprivileged public route or command shape, violating the invariant that unprivileged callers must not reach privileged daemon, keychain, or wallet actions and leading to Bypass of wallet, daemon, keychain, RPC, pool, or Data Layer authorization that enables unauthorized signing, key use, coin control, payout redirection, singleton mutation, or protected state transitions?

## Target
- File/function: chia/wallet/wallet_rpc_api.py:3136 `WalletRpcApi.create_signed_transaction`
- Entrypoint: RPC route `create_signed_transaction`
- Attacker controls: public RPC or WebSocket command arguments that select protected actions
- Exploit idea: reach a privileged path in `create_signed_transaction` from a nominally unprivileged public route or command shape
- Invariant to test: unprivileged callers must not reach privileged daemon, keychain, or wallet actions
- Expected Immunefi impact: Bypass of wallet, daemon, keychain, RPC, pool, or Data Layer authorization that enables unauthorized signing, key use, coin control, payout redirection, singleton mutation, or protected state transitions
- Fast validation: invoke `chia/wallet/wallet_rpc_api.py:create_signed_transaction` through its public command path with unprivileged inputs and assert privilege checks fail before state changes
