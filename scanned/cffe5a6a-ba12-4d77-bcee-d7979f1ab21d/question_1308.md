# Q1308: get_mempool_items_by_coin_name redirects pool rewards or singleton transitions

## Question
Can an unprivileged attacker reach RPC route `get_mempool_items_by_coin_name` and control pool singleton state, payout instructions, reward claims, and absorb timing so that `FullNodeRpcApi.get_mempool_items_by_coin_name` in `chia/full_node/full_node_rpc_api.py` executes a path where make `get_mempool_items_by_coin_name` redirect pool rewards or singleton state transitions away from the rightful owner, violating the invariant that pool reward claims and singleton transitions must only benefit the rightful singleton owner and leading to Bypass of wallet, daemon, keychain, RPC, pool, or Data Layer authorization that enables unauthorized signing, key use, coin control, payout redirection, singleton mutation, or protected state transitions?

## Target
- File/function: chia/full_node/full_node_rpc_api.py:958 `FullNodeRpcApi.get_mempool_items_by_coin_name`
- Entrypoint: RPC route `get_mempool_items_by_coin_name`
- Attacker controls: pool singleton state, payout instructions, reward claims, and absorb timing
- Exploit idea: make `get_mempool_items_by_coin_name` redirect pool rewards or singleton state transitions away from the rightful owner
- Invariant to test: pool reward claims and singleton transitions must only benefit the rightful singleton owner
- Expected Immunefi impact: Bypass of wallet, daemon, keychain, RPC, pool, or Data Layer authorization that enables unauthorized signing, key use, coin control, payout redirection, singleton mutation, or protected state transitions
- Fast validation: simulate absorb or claim flows in `chia/full_node/full_node_rpc_api.py:get_mempool_items_by_coin_name` with swapped payout state and assert rewards cannot redirect
