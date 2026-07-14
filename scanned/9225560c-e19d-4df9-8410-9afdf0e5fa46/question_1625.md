# Q1625: new_signage_point_harvester applies the wrong privilege boundary to a public route

## Question
Can an unprivileged attacker reach P2P message handler `new_signage_point_harvester` and control public RPC or WebSocket command arguments that select protected actions so that `HarvesterAPI.new_signage_point_harvester` in `chia/harvester/harvester_api.py` executes a path where reach a privileged path in `new_signage_point_harvester` from a nominally unprivileged public route or command shape, violating the invariant that unprivileged callers must not reach privileged daemon, keychain, or wallet actions and leading to Bypass of wallet, daemon, keychain, RPC, pool, or Data Layer authorization that enables unauthorized signing, key use, coin control, payout redirection, singleton mutation, or protected state transitions?

## Target
- File/function: chia/harvester/harvester_api.py:130 `HarvesterAPI.new_signage_point_harvester`
- Entrypoint: P2P message handler `new_signage_point_harvester`
- Attacker controls: public RPC or WebSocket command arguments that select protected actions
- Exploit idea: reach a privileged path in `new_signage_point_harvester` from a nominally unprivileged public route or command shape
- Invariant to test: unprivileged callers must not reach privileged daemon, keychain, or wallet actions
- Expected Immunefi impact: Bypass of wallet, daemon, keychain, RPC, pool, or Data Layer authorization that enables unauthorized signing, key use, coin control, payout redirection, singleton mutation, or protected state transitions
- Fast validation: invoke `chia/harvester/harvester_api.py:new_signage_point_harvester` through its public command path with unprivileged inputs and assert privilege checks fail before state changes
