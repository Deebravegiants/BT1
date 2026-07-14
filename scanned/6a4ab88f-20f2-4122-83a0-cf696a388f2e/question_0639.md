# Q639: get_signage_points applies the wrong privilege boundary to a public route

## Question
Can an unprivileged attacker reach RPC route `get_signage_points` and control public RPC or WebSocket command arguments that select protected actions so that `FarmerRpcApi.get_signage_points` in `chia/farmer/farmer_rpc_api.py` executes a path where reach a privileged path in `get_signage_points` from a nominally unprivileged public route or command shape, violating the invariant that unprivileged callers must not reach privileged daemon, keychain, or wallet actions and leading to Bypass of wallet, daemon, keychain, RPC, pool, or Data Layer authorization that enables unauthorized signing, key use, coin control, payout redirection, singleton mutation, or protected state transitions?

## Target
- File/function: chia/farmer/farmer_rpc_api.py:266 `FarmerRpcApi.get_signage_points`
- Entrypoint: RPC route `get_signage_points`
- Attacker controls: public RPC or WebSocket command arguments that select protected actions
- Exploit idea: reach a privileged path in `get_signage_points` from a nominally unprivileged public route or command shape
- Invariant to test: unprivileged callers must not reach privileged daemon, keychain, or wallet actions
- Expected Immunefi impact: Bypass of wallet, daemon, keychain, RPC, pool, or Data Layer authorization that enables unauthorized signing, key use, coin control, payout redirection, singleton mutation, or protected state transitions
- Fast validation: invoke `chia/farmer/farmer_rpc_api.py:get_signage_points` through its public command path with unprivileged inputs and assert privilege checks fail before state changes
