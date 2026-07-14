# Q763: add_mempool_item accepts a pool membership transition with stale or swapped state

## Question
Can an unprivileged attacker reach full node mempool, sync, or peer flow reaching `add_mempool_item` and control launcher ids, pool target state, delayed puzzle data, and join/leave sequencing so that `FeeEstimatorInterface.add_mempool_item` in `chia/full_node/fee_estimator_interface.py` executes a path where make `add_mempool_item` apply pool join, leave, or waiting-room state under swapped singleton context, violating the invariant that pool membership state must advance only through canonical singleton transitions and leading to Bypass of wallet, daemon, keychain, RPC, pool, or Data Layer authorization that enables unauthorized signing, key use, coin control, payout redirection, singleton mutation, or protected state transitions?

## Target
- File/function: chia/full_node/fee_estimator_interface.py:18 `FeeEstimatorInterface.add_mempool_item`
- Entrypoint: full node mempool, sync, or peer flow reaching `add_mempool_item`
- Attacker controls: launcher ids, pool target state, delayed puzzle data, and join/leave sequencing
- Exploit idea: make `add_mempool_item` apply pool join, leave, or waiting-room state under swapped singleton context
- Invariant to test: pool membership state must advance only through canonical singleton transitions
- Expected Immunefi impact: Bypass of wallet, daemon, keychain, RPC, pool, or Data Layer authorization that enables unauthorized signing, key use, coin control, payout redirection, singleton mutation, or protected state transitions
- Fast validation: drive join/leave transitions with stale singleton context into `chia/full_node/fee_estimator_interface.py:add_mempool_item` and assert state changes reject cleanly
