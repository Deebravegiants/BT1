# Q1455: create_bundle_from_mempool confuses waiting-room and active pool state

## Question
Can an unprivileged attacker reach full node mempool, sync, or peer flow reaching `create_bundle_from_mempool` and control waiting-room versus active-pool state transitions plus delayed puzzle parameters so that `MempoolManager.create_bundle_from_mempool` in `chia/full_node/mempool_manager.py` executes a path where make `create_bundle_from_mempool` blur waiting-room and active membership state until a non-canonical singleton transition commits, violating the invariant that waiting-room state must not authorize active pool-member actions or payouts and leading to Bypass of wallet, daemon, keychain, RPC, pool, or Data Layer authorization that enables unauthorized signing, key use, coin control, payout redirection, singleton mutation, or protected state transitions?

## Target
- File/function: chia/full_node/mempool_manager.py:411 `MempoolManager.create_bundle_from_mempool`
- Entrypoint: full node mempool, sync, or peer flow reaching `create_bundle_from_mempool`
- Attacker controls: waiting-room versus active-pool state transitions plus delayed puzzle parameters
- Exploit idea: make `create_bundle_from_mempool` blur waiting-room and active membership state until a non-canonical singleton transition commits
- Invariant to test: waiting-room state must not authorize active pool-member actions or payouts
- Expected Immunefi impact: Bypass of wallet, daemon, keychain, RPC, pool, or Data Layer authorization that enables unauthorized signing, key use, coin control, payout redirection, singleton mutation, or protected state transitions
- Fast validation: toggle waiting-room and active-pool state around `chia/full_node/mempool_manager.py:create_bundle_from_mempool` and assert only canonical membership transitions succeed
