# Q599: respond_signatures applies the wrong privilege boundary to a public route

## Question
Can an unprivileged attacker reach P2P message handler `respond_signatures` and control public RPC or WebSocket command arguments that select protected actions so that `FarmerAPI.respond_signatures` in `chia/farmer/farmer_api.py` executes a path where reach a privileged path in `respond_signatures` from a nominally unprivileged public route or command shape, violating the invariant that unprivileged callers must not reach privileged daemon, keychain, or wallet actions and leading to Bypass of wallet, daemon, keychain, RPC, pool, or Data Layer authorization that enables unauthorized signing, key use, coin control, payout redirection, singleton mutation, or protected state transitions?

## Target
- File/function: chia/farmer/farmer_api.py:603 `FarmerAPI.respond_signatures`
- Entrypoint: P2P message handler `respond_signatures`
- Attacker controls: public RPC or WebSocket command arguments that select protected actions
- Exploit idea: reach a privileged path in `respond_signatures` from a nominally unprivileged public route or command shape
- Invariant to test: unprivileged callers must not reach privileged daemon, keychain, or wallet actions
- Expected Immunefi impact: Bypass of wallet, daemon, keychain, RPC, pool, or Data Layer authorization that enables unauthorized signing, key use, coin control, payout redirection, singleton mutation, or protected state transitions
- Fast validation: invoke `chia/farmer/farmer_api.py:respond_signatures` through its public command path with unprivileged inputs and assert privilege checks fail before state changes
