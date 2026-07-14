# Q1434: create_bundle_from_mempool_items confuses waiting-room and active pool state

## Question
Can an unprivileged attacker reach full node mempool, sync, or peer flow reaching `create_bundle_from_mempool_items` and control waiting-room versus active-pool state transitions plus delayed puzzle parameters so that `Mempool.create_bundle_from_mempool_items` in `chia/full_node/mempool.py` executes a path where make `create_bundle_from_mempool_items` blur waiting-room and active membership state until a non-canonical singleton transition commits, violating the invariant that waiting-room state must not authorize active pool-member actions or payouts and leading to Bypass of wallet, daemon, keychain, RPC, pool, or Data Layer authorization that enables unauthorized signing, key use, coin control, payout redirection, singleton mutation, or protected state transitions?

## Target
- File/function: chia/full_node/mempool.py:583 `Mempool.create_bundle_from_mempool_items`
- Entrypoint: full node mempool, sync, or peer flow reaching `create_bundle_from_mempool_items`
- Attacker controls: waiting-room versus active-pool state transitions plus delayed puzzle parameters
- Exploit idea: make `create_bundle_from_mempool_items` blur waiting-room and active membership state until a non-canonical singleton transition commits
- Invariant to test: waiting-room state must not authorize active pool-member actions or payouts
- Expected Immunefi impact: Bypass of wallet, daemon, keychain, RPC, pool, or Data Layer authorization that enables unauthorized signing, key use, coin control, payout redirection, singleton mutation, or protected state transitions
- Fast validation: toggle waiting-room and active-pool state around `chia/full_node/mempool.py:create_bundle_from_mempool_items` and assert only canonical membership transitions succeed
