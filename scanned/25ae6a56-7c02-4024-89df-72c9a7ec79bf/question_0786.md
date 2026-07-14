# Q786: new_mempool_tx confuses waiting-room and active pool state

## Question
Can an unprivileged attacker reach full node mempool, sync, or peer flow reaching `new_mempool_tx` and control waiting-room versus active-pool state transitions plus delayed puzzle parameters so that `FeeStat.new_mempool_tx` in `chia/full_node/fee_tracker.py` executes a path where make `new_mempool_tx` blur waiting-room and active membership state until a non-canonical singleton transition commits, violating the invariant that waiting-room state must not authorize active pool-member actions or payouts and leading to Bypass of wallet, daemon, keychain, RPC, pool, or Data Layer authorization that enables unauthorized signing, key use, coin control, payout redirection, singleton mutation, or protected state transitions?

## Target
- File/function: chia/full_node/fee_tracker.py:162 `FeeStat.new_mempool_tx`
- Entrypoint: full node mempool, sync, or peer flow reaching `new_mempool_tx`
- Attacker controls: waiting-room versus active-pool state transitions plus delayed puzzle parameters
- Exploit idea: make `new_mempool_tx` blur waiting-room and active membership state until a non-canonical singleton transition commits
- Invariant to test: waiting-room state must not authorize active pool-member actions or payouts
- Expected Immunefi impact: Bypass of wallet, daemon, keychain, RPC, pool, or Data Layer authorization that enables unauthorized signing, key use, coin control, payout redirection, singleton mutation, or protected state transitions
- Fast validation: toggle waiting-room and active-pool state around `chia/full_node/fee_tracker.py:new_mempool_tx` and assert only canonical membership transitions succeed
