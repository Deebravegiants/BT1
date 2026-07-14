# Q1398: remove_from_pool confuses waiting-room and active pool state

## Question
Can an unprivileged attacker reach full node mempool, sync, or peer flow reaching `remove_from_pool` and control waiting-room versus active-pool state transitions plus delayed puzzle parameters so that `Mempool.remove_from_pool` in `chia/full_node/mempool.py` executes a path where make `remove_from_pool` blur waiting-room and active membership state until a non-canonical singleton transition commits, violating the invariant that waiting-room state must not authorize active pool-member actions or payouts and leading to Bypass of wallet, daemon, keychain, RPC, pool, or Data Layer authorization that enables unauthorized signing, key use, coin control, payout redirection, singleton mutation, or protected state transitions?

## Target
- File/function: chia/full_node/mempool.py:347 `Mempool.remove_from_pool`
- Entrypoint: full node mempool, sync, or peer flow reaching `remove_from_pool`
- Attacker controls: waiting-room versus active-pool state transitions plus delayed puzzle parameters
- Exploit idea: make `remove_from_pool` blur waiting-room and active membership state until a non-canonical singleton transition commits
- Invariant to test: waiting-room state must not authorize active pool-member actions or payouts
- Expected Immunefi impact: Bypass of wallet, daemon, keychain, RPC, pool, or Data Layer authorization that enables unauthorized signing, key use, coin control, payout redirection, singleton mutation, or protected state transitions
- Fast validation: toggle waiting-room and active-pool state around `chia/full_node/mempool.py:remove_from_pool` and assert only canonical membership transitions succeed
