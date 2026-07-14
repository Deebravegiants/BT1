# Q775: remove_mempool_item confuses waiting-room and active pool state

## Question
Can an unprivileged attacker reach full node mempool, sync, or peer flow reaching `remove_mempool_item` and control waiting-room versus active-pool state transitions plus delayed puzzle parameters so that `FeeEstimatorInterface.remove_mempool_item` in `chia/full_node/fee_estimator_interface.py` executes a path where make `remove_mempool_item` blur waiting-room and active membership state until a non-canonical singleton transition commits, violating the invariant that waiting-room state must not authorize active pool-member actions or payouts and leading to Bypass of wallet, daemon, keychain, RPC, pool, or Data Layer authorization that enables unauthorized signing, key use, coin control, payout redirection, singleton mutation, or protected state transitions?

## Target
- File/function: chia/full_node/fee_estimator_interface.py:21 `FeeEstimatorInterface.remove_mempool_item`
- Entrypoint: full node mempool, sync, or peer flow reaching `remove_mempool_item`
- Attacker controls: waiting-room versus active-pool state transitions plus delayed puzzle parameters
- Exploit idea: make `remove_mempool_item` blur waiting-room and active membership state until a non-canonical singleton transition commits
- Invariant to test: waiting-room state must not authorize active pool-member actions or payouts
- Expected Immunefi impact: Bypass of wallet, daemon, keychain, RPC, pool, or Data Layer authorization that enables unauthorized signing, key use, coin control, payout redirection, singleton mutation, or protected state transitions
- Fast validation: toggle waiting-room and active-pool state around `chia/full_node/fee_estimator_interface.py:remove_mempool_item` and assert only canonical membership transitions succeed
