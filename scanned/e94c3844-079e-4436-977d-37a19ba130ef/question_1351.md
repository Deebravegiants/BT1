# Q1351: new_signage_point applies the wrong privilege boundary to a public route

## Question
Can an unprivileged attacker reach full node mempool, sync, or peer flow reaching `new_signage_point` and control public RPC or WebSocket command arguments that select protected actions so that `FullNodeStore.new_signage_point` in `chia/full_node/full_node_store.py` executes a path where reach a privileged path in `new_signage_point` from a nominally unprivileged public route or command shape, violating the invariant that unprivileged callers must not reach privileged daemon, keychain, or wallet actions and leading to Bypass of wallet, daemon, keychain, RPC, pool, or Data Layer authorization that enables unauthorized signing, key use, coin control, payout redirection, singleton mutation, or protected state transitions?

## Target
- File/function: chia/full_node/full_node_store.py:709 `FullNodeStore.new_signage_point`
- Entrypoint: full node mempool, sync, or peer flow reaching `new_signage_point`
- Attacker controls: public RPC or WebSocket command arguments that select protected actions
- Exploit idea: reach a privileged path in `new_signage_point` from a nominally unprivileged public route or command shape
- Invariant to test: unprivileged callers must not reach privileged daemon, keychain, or wallet actions
- Expected Immunefi impact: Bypass of wallet, daemon, keychain, RPC, pool, or Data Layer authorization that enables unauthorized signing, key use, coin control, payout redirection, singleton mutation, or protected state transitions
- Fast validation: invoke `chia/full_node/full_node_store.py:new_signage_point` through its public command path with unprivileged inputs and assert privilege checks fail before state changes
