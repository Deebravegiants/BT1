# Q1701: join_pool confuses waiting-room and active pool state

## Question
Can an unprivileged attacker reach pool wallet or singleton spend flow reaching `join_pool` and control waiting-room versus active-pool state transitions plus delayed puzzle parameters so that `PlotNFT.join_pool` in `chia/pools/plotnft_drivers.py` executes a path where make `join_pool` blur waiting-room and active membership state until a non-canonical singleton transition commits, violating the invariant that waiting-room state must not authorize active pool-member actions or payouts and leading to Bypass of wallet, daemon, keychain, RPC, pool, or Data Layer authorization that enables unauthorized signing, key use, coin control, payout redirection, singleton mutation, or protected state transitions?

## Target
- File/function: chia/pools/plotnft_drivers.py:643 `PlotNFT.join_pool`
- Entrypoint: pool wallet or singleton spend flow reaching `join_pool`
- Attacker controls: waiting-room versus active-pool state transitions plus delayed puzzle parameters
- Exploit idea: make `join_pool` blur waiting-room and active membership state until a non-canonical singleton transition commits
- Invariant to test: waiting-room state must not authorize active pool-member actions or payouts
- Expected Immunefi impact: Bypass of wallet, daemon, keychain, RPC, pool, or Data Layer authorization that enables unauthorized signing, key use, coin control, payout redirection, singleton mutation, or protected state transitions
- Fast validation: toggle waiting-room and active-pool state around `chia/pools/plotnft_drivers.py:join_pool` and assert only canonical membership transitions succeed
