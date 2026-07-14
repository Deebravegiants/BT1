# Q617: request_signed_values applies the wrong privilege boundary to a public route

## Question
Can an unprivileged attacker reach P2P message handler `request_signed_values` and control public RPC or WebSocket command arguments that select protected actions so that `FarmerAPI.request_signed_values` in `chia/farmer/farmer_api.py` executes a path where reach a privileged path in `request_signed_values` from a nominally unprivileged public route or command shape, violating the invariant that unprivileged callers must not reach privileged daemon, keychain, or wallet actions and leading to Bypass of wallet, daemon, keychain, RPC, pool, or Data Layer authorization that enables unauthorized signing, key use, coin control, payout redirection, singleton mutation, or protected state transitions?

## Target
- File/function: chia/farmer/farmer_api.py:723 `FarmerAPI.request_signed_values`
- Entrypoint: P2P message handler `request_signed_values`
- Attacker controls: public RPC or WebSocket command arguments that select protected actions
- Exploit idea: reach a privileged path in `request_signed_values` from a nominally unprivileged public route or command shape
- Invariant to test: unprivileged callers must not reach privileged daemon, keychain, or wallet actions
- Expected Immunefi impact: Bypass of wallet, daemon, keychain, RPC, pool, or Data Layer authorization that enables unauthorized signing, key use, coin control, payout redirection, singleton mutation, or protected state transitions
- Fast validation: invoke `chia/farmer/farmer_api.py:request_signed_values` through its public command path with unprivileged inputs and assert privilege checks fail before state changes
