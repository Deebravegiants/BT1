# Q1664: claim_pool_reward_dpuz confuses waiting-room and active pool state

## Question
Can an unprivileged attacker reach pool wallet or singleton spend flow reaching `claim_pool_reward_dpuz` and control waiting-room versus active-pool state transitions plus delayed puzzle parameters so that `PlotNFTPuzzle.claim_pool_reward_dpuz` in `chia/pools/plotnft_drivers.py` executes a path where make `claim_pool_reward_dpuz` blur waiting-room and active membership state until a non-canonical singleton transition commits, violating the invariant that waiting-room state must not authorize active pool-member actions or payouts and leading to Bypass of wallet, daemon, keychain, RPC, pool, or Data Layer authorization that enables unauthorized signing, key use, coin control, payout redirection, singleton mutation, or protected state transitions?

## Target
- File/function: chia/pools/plotnft_drivers.py:153 `PlotNFTPuzzle.claim_pool_reward_dpuz`
- Entrypoint: pool wallet or singleton spend flow reaching `claim_pool_reward_dpuz`
- Attacker controls: waiting-room versus active-pool state transitions plus delayed puzzle parameters
- Exploit idea: make `claim_pool_reward_dpuz` blur waiting-room and active membership state until a non-canonical singleton transition commits
- Invariant to test: waiting-room state must not authorize active pool-member actions or payouts
- Expected Immunefi impact: Bypass of wallet, daemon, keychain, RPC, pool, or Data Layer authorization that enables unauthorized signing, key use, coin control, payout redirection, singleton mutation, or protected state transitions
- Fast validation: toggle waiting-room and active-pool state around `chia/pools/plotnft_drivers.py:claim_pool_reward_dpuz` and assert only canonical membership transitions succeed
