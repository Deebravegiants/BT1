# Q1401: add_to_pool accepts a pool membership transition with stale or swapped state

## Question
Can an unprivileged attacker reach full node mempool, sync, or peer flow reaching `add_to_pool` and control launcher ids, pool target state, delayed puzzle data, and join/leave sequencing so that `Mempool.add_to_pool` in `chia/full_node/mempool.py` executes a path where make `add_to_pool` apply pool join, leave, or waiting-room state under swapped singleton context, violating the invariant that pool membership state must advance only through canonical singleton transitions and leading to Bypass of wallet, daemon, keychain, RPC, pool, or Data Layer authorization that enables unauthorized signing, key use, coin control, payout redirection, singleton mutation, or protected state transitions?

## Target
- File/function: chia/full_node/mempool.py:395 `Mempool.add_to_pool`
- Entrypoint: full node mempool, sync, or peer flow reaching `add_to_pool`
- Attacker controls: launcher ids, pool target state, delayed puzzle data, and join/leave sequencing
- Exploit idea: make `add_to_pool` apply pool join, leave, or waiting-room state under swapped singleton context
- Invariant to test: pool membership state must advance only through canonical singleton transitions
- Expected Immunefi impact: Bypass of wallet, daemon, keychain, RPC, pool, or Data Layer authorization that enables unauthorized signing, key use, coin control, payout redirection, singleton mutation, or protected state transitions
- Fast validation: drive join/leave transitions with stale singleton context into `chia/full_node/mempool.py:add_to_pool` and assert state changes reject cleanly
