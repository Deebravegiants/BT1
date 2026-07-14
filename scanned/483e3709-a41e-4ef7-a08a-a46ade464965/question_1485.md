# Q1485: add_spend_bundle accepts a pool membership transition with stale or swapped state

## Question
Can an unprivileged attacker reach full node mempool, sync, or peer flow reaching `add_spend_bundle` and control launcher ids, pool target state, delayed puzzle data, and join/leave sequencing so that `MempoolManager.add_spend_bundle` in `chia/full_node/mempool_manager.py` executes a path where make `add_spend_bundle` apply pool join, leave, or waiting-room state under swapped singleton context, violating the invariant that pool membership state must advance only through canonical singleton transitions and leading to Bypass of wallet, daemon, keychain, RPC, pool, or Data Layer authorization that enables unauthorized signing, key use, coin control, payout redirection, singleton mutation, or protected state transitions?

## Target
- File/function: chia/full_node/mempool_manager.py:552 `MempoolManager.add_spend_bundle`
- Entrypoint: full node mempool, sync, or peer flow reaching `add_spend_bundle`
- Attacker controls: launcher ids, pool target state, delayed puzzle data, and join/leave sequencing
- Exploit idea: make `add_spend_bundle` apply pool join, leave, or waiting-room state under swapped singleton context
- Invariant to test: pool membership state must advance only through canonical singleton transitions
- Expected Immunefi impact: Bypass of wallet, daemon, keychain, RPC, pool, or Data Layer authorization that enables unauthorized signing, key use, coin control, payout redirection, singleton mutation, or protected state transitions
- Fast validation: drive join/leave transitions with stale singleton context into `chia/full_node/mempool_manager.py:add_spend_bundle` and assert state changes reject cleanly
