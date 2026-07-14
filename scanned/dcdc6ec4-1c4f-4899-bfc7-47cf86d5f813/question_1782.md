# Q1782: update_pool_config confuses waiting-room and active pool state

## Question
Can an unprivileged attacker reach pool wallet or singleton spend flow reaching `update_pool_config` and control waiting-room versus active-pool state transitions plus delayed puzzle parameters so that `PoolWallet.update_pool_config` in `chia/pools/pool_wallet.py` executes a path where make `update_pool_config` blur waiting-room and active membership state until a non-canonical singleton transition commits, violating the invariant that waiting-room state must not authorize active pool-member actions or payouts and leading to Bypass of wallet, daemon, keychain, RPC, pool, or Data Layer authorization that enables unauthorized signing, key use, coin control, payout redirection, singleton mutation, or protected state transitions?

## Target
- File/function: chia/pools/pool_wallet.py:231 `PoolWallet.update_pool_config`
- Entrypoint: pool wallet or singleton spend flow reaching `update_pool_config`
- Attacker controls: waiting-room versus active-pool state transitions plus delayed puzzle parameters
- Exploit idea: make `update_pool_config` blur waiting-room and active membership state until a non-canonical singleton transition commits
- Invariant to test: waiting-room state must not authorize active pool-member actions or payouts
- Expected Immunefi impact: Bypass of wallet, daemon, keychain, RPC, pool, or Data Layer authorization that enables unauthorized signing, key use, coin control, payout redirection, singleton mutation, or protected state transitions
- Fast validation: toggle waiting-room and active-pool state around `chia/pools/pool_wallet.py:update_pool_config` and assert only canonical membership transitions succeed
