# Q1298: get_mempool_item_by_tx_id accepts a pool membership transition with stale or swapped state

## Question
Can an unprivileged attacker reach RPC route `get_mempool_item_by_tx_id` and control launcher ids, pool target state, delayed puzzle data, and join/leave sequencing so that `FullNodeRpcApi.get_mempool_item_by_tx_id` in `chia/full_node/full_node_rpc_api.py` executes a path where make `get_mempool_item_by_tx_id` apply pool join, leave, or waiting-room state under swapped singleton context, violating the invariant that pool membership state must advance only through canonical singleton transitions and leading to Bypass of wallet, daemon, keychain, RPC, pool, or Data Layer authorization that enables unauthorized signing, key use, coin control, payout redirection, singleton mutation, or protected state transitions?

## Target
- File/function: chia/full_node/full_node_rpc_api.py:941 `FullNodeRpcApi.get_mempool_item_by_tx_id`
- Entrypoint: RPC route `get_mempool_item_by_tx_id`
- Attacker controls: launcher ids, pool target state, delayed puzzle data, and join/leave sequencing
- Exploit idea: make `get_mempool_item_by_tx_id` apply pool join, leave, or waiting-room state under swapped singleton context
- Invariant to test: pool membership state must advance only through canonical singleton transitions
- Expected Immunefi impact: Bypass of wallet, daemon, keychain, RPC, pool, or Data Layer authorization that enables unauthorized signing, key use, coin control, payout redirection, singleton mutation, or protected state transitions
- Fast validation: drive join/leave transitions with stale singleton context into `chia/full_node/full_node_rpc_api.py:get_mempool_item_by_tx_id` and assert state changes reject cleanly
