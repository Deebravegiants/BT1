# Q1474: create_block_generator2 accepts a pool membership transition with stale or swapped state

## Question
Can an unprivileged attacker reach full node mempool, sync, or peer flow reaching `create_block_generator2` and control launcher ids, pool target state, delayed puzzle data, and join/leave sequencing so that `MempoolManager.create_block_generator2` in `chia/full_node/mempool_manager.py` executes a path where make `create_block_generator2` apply pool join, leave, or waiting-room state under swapped singleton context, violating the invariant that pool membership state must advance only through canonical singleton transitions and leading to Bypass of wallet, daemon, keychain, RPC, pool, or Data Layer authorization that enables unauthorized signing, key use, coin control, payout redirection, singleton mutation, or protected state transitions?

## Target
- File/function: chia/full_node/mempool_manager.py:428 `MempoolManager.create_block_generator2`
- Entrypoint: full node mempool, sync, or peer flow reaching `create_block_generator2`
- Attacker controls: launcher ids, pool target state, delayed puzzle data, and join/leave sequencing
- Exploit idea: make `create_block_generator2` apply pool join, leave, or waiting-room state under swapped singleton context
- Invariant to test: pool membership state must advance only through canonical singleton transitions
- Expected Immunefi impact: Bypass of wallet, daemon, keychain, RPC, pool, or Data Layer authorization that enables unauthorized signing, key use, coin control, payout redirection, singleton mutation, or protected state transitions
- Fast validation: drive join/leave transitions with stale singleton context into `chia/full_node/mempool_manager.py:create_block_generator2` and assert state changes reject cleanly
