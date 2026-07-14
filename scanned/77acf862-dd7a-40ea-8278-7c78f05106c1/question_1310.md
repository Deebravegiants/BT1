# Q1310: get_mempool_items_by_coin_name confuses waiting-room and active pool state

## Question
Can an unprivileged attacker reach RPC route `get_mempool_items_by_coin_name` and control waiting-room versus active-pool state transitions plus delayed puzzle parameters so that `FullNodeRpcApi.get_mempool_items_by_coin_name` in `chia/full_node/full_node_rpc_api.py` executes a path where make `get_mempool_items_by_coin_name` blur waiting-room and active membership state until a non-canonical singleton transition commits, violating the invariant that waiting-room state must not authorize active pool-member actions or payouts and leading to Bypass of wallet, daemon, keychain, RPC, pool, or Data Layer authorization that enables unauthorized signing, key use, coin control, payout redirection, singleton mutation, or protected state transitions?

## Target
- File/function: chia/full_node/full_node_rpc_api.py:958 `FullNodeRpcApi.get_mempool_items_by_coin_name`
- Entrypoint: RPC route `get_mempool_items_by_coin_name`
- Attacker controls: waiting-room versus active-pool state transitions plus delayed puzzle parameters
- Exploit idea: make `get_mempool_items_by_coin_name` blur waiting-room and active membership state until a non-canonical singleton transition commits
- Invariant to test: waiting-room state must not authorize active pool-member actions or payouts
- Expected Immunefi impact: Bypass of wallet, daemon, keychain, RPC, pool, or Data Layer authorization that enables unauthorized signing, key use, coin control, payout redirection, singleton mutation, or protected state transitions
- Fast validation: toggle waiting-room and active-pool state around `chia/full_node/full_node_rpc_api.py:get_mempool_items_by_coin_name` and assert only canonical membership transitions succeed
