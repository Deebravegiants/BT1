# Q1087: new_signage_point_vdf applies the wrong privilege boundary to a public route

## Question
Can an unprivileged attacker reach P2P message handler `new_signage_point_vdf` and control public RPC or WebSocket command arguments that select protected actions so that `FullNodeAPI.new_signage_point_vdf` in `chia/full_node/full_node_api.py` executes a path where reach a privileged path in `new_signage_point_vdf` from a nominally unprivileged public route or command shape, violating the invariant that unprivileged callers must not reach privileged daemon, keychain, or wallet actions and leading to Bypass of wallet, daemon, keychain, RPC, pool, or Data Layer authorization that enables unauthorized signing, key use, coin control, payout redirection, singleton mutation, or protected state transitions?

## Target
- File/function: chia/full_node/full_node_api.py:1301 `FullNodeAPI.new_signage_point_vdf`
- Entrypoint: P2P message handler `new_signage_point_vdf`
- Attacker controls: public RPC or WebSocket command arguments that select protected actions
- Exploit idea: reach a privileged path in `new_signage_point_vdf` from a nominally unprivileged public route or command shape
- Invariant to test: unprivileged callers must not reach privileged daemon, keychain, or wallet actions
- Expected Immunefi impact: Bypass of wallet, daemon, keychain, RPC, pool, or Data Layer authorization that enables unauthorized signing, key use, coin control, payout redirection, singleton mutation, or protected state transitions
- Fast validation: invoke `chia/full_node/full_node_api.py:new_signage_point_vdf` through its public command path with unprivileged inputs and assert privilege checks fail before state changes
