# Q785: new_mempool_tx accepts a pool membership transition with stale or swapped state

## Question
Can an unprivileged attacker reach full node mempool, sync, or peer flow reaching `new_mempool_tx` and control launcher ids, pool target state, delayed puzzle data, and join/leave sequencing so that `FeeStat.new_mempool_tx` in `chia/full_node/fee_tracker.py` executes a path where make `new_mempool_tx` apply pool join, leave, or waiting-room state under swapped singleton context, violating the invariant that pool membership state must advance only through canonical singleton transitions and leading to Bypass of wallet, daemon, keychain, RPC, pool, or Data Layer authorization that enables unauthorized signing, key use, coin control, payout redirection, singleton mutation, or protected state transitions?

## Target
- File/function: chia/full_node/fee_tracker.py:162 `FeeStat.new_mempool_tx`
- Entrypoint: full node mempool, sync, or peer flow reaching `new_mempool_tx`
- Attacker controls: launcher ids, pool target state, delayed puzzle data, and join/leave sequencing
- Exploit idea: make `new_mempool_tx` apply pool join, leave, or waiting-room state under swapped singleton context
- Invariant to test: pool membership state must advance only through canonical singleton transitions
- Expected Immunefi impact: Bypass of wallet, daemon, keychain, RPC, pool, or Data Layer authorization that enables unauthorized signing, key use, coin control, payout redirection, singleton mutation, or protected state transitions
- Fast validation: drive join/leave transitions with stale singleton context into `chia/full_node/fee_tracker.py:new_mempool_tx` and assert state changes reject cleanly
