# Q1053: request_mempool_transactions confuses waiting-room and active pool state

## Question
Can an unprivileged attacker reach P2P message handler `request_mempool_transactions` and control waiting-room versus active-pool state transitions plus delayed puzzle parameters so that `FullNodeAPI.request_mempool_transactions` in `chia/full_node/full_node_api.py` executes a path where make `request_mempool_transactions` blur waiting-room and active membership state until a non-canonical singleton transition commits, violating the invariant that waiting-room state must not authorize active pool-member actions or payouts and leading to Bypass of wallet, daemon, keychain, RPC, pool, or Data Layer authorization that enables unauthorized signing, key use, coin control, payout redirection, singleton mutation, or protected state transitions?

## Target
- File/function: chia/full_node/full_node_api.py:875 `FullNodeAPI.request_mempool_transactions`
- Entrypoint: P2P message handler `request_mempool_transactions`
- Attacker controls: waiting-room versus active-pool state transitions plus delayed puzzle parameters
- Exploit idea: make `request_mempool_transactions` blur waiting-room and active membership state until a non-canonical singleton transition commits
- Invariant to test: waiting-room state must not authorize active pool-member actions or payouts
- Expected Immunefi impact: Bypass of wallet, daemon, keychain, RPC, pool, or Data Layer authorization that enables unauthorized signing, key use, coin control, payout redirection, singleton mutation, or protected state transitions
- Fast validation: toggle waiting-room and active-pool state around `chia/full_node/full_node_api.py:request_mempool_transactions` and assert only canonical membership transitions succeed
