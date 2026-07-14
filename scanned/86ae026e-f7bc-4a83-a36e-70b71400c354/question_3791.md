# Q3791: sign_message_by_id applies the wrong privilege boundary to a public route

## Question
Can an unprivileged attacker reach RPC route `sign_message_by_id` and control public RPC or WebSocket command arguments that select protected actions so that `WalletRpcApi.sign_message_by_id` in `chia/wallet/wallet_rpc_api.py` executes a path where reach a privileged path in `sign_message_by_id` from a nominally unprivileged public route or command shape, violating the invariant that unprivileged callers must not reach privileged daemon, keychain, or wallet actions and leading to Bypass of wallet, daemon, keychain, RPC, pool, or Data Layer authorization that enables unauthorized signing, key use, coin control, payout redirection, singleton mutation, or protected state transitions?

## Target
- File/function: chia/wallet/wallet_rpc_api.py:1920 `WalletRpcApi.sign_message_by_id`
- Entrypoint: RPC route `sign_message_by_id`
- Attacker controls: public RPC or WebSocket command arguments that select protected actions
- Exploit idea: reach a privileged path in `sign_message_by_id` from a nominally unprivileged public route or command shape
- Invariant to test: unprivileged callers must not reach privileged daemon, keychain, or wallet actions
- Expected Immunefi impact: Bypass of wallet, daemon, keychain, RPC, pool, or Data Layer authorization that enables unauthorized signing, key use, coin control, payout redirection, singleton mutation, or protected state transitions
- Fast validation: invoke `chia/wallet/wallet_rpc_api.py:sign_message_by_id` through its public command path with unprivileged inputs and assert privilege checks fail before state changes
