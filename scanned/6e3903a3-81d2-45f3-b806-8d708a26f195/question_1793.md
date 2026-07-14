# Q1793: create_new_pool_wallet_transaction confuses waiting-room and active pool state

## Question
Can an unprivileged attacker reach pool wallet or singleton spend flow reaching `create_new_pool_wallet_transaction` and control waiting-room versus active-pool state transitions plus delayed puzzle parameters so that `PoolWallet.create_new_pool_wallet_transaction` in `chia/pools/pool_wallet.py` executes a path where make `create_new_pool_wallet_transaction` blur waiting-room and active membership state until a non-canonical singleton transition commits, violating the invariant that waiting-room state must not authorize active pool-member actions or payouts and leading to Bypass of wallet, daemon, keychain, RPC, pool, or Data Layer authorization that enables unauthorized signing, key use, coin control, payout redirection, singleton mutation, or protected state transitions?

## Target
- File/function: chia/pools/pool_wallet.py:391 `PoolWallet.create_new_pool_wallet_transaction`
- Entrypoint: pool wallet or singleton spend flow reaching `create_new_pool_wallet_transaction`
- Attacker controls: waiting-room versus active-pool state transitions plus delayed puzzle parameters
- Exploit idea: make `create_new_pool_wallet_transaction` blur waiting-room and active membership state until a non-canonical singleton transition commits
- Invariant to test: waiting-room state must not authorize active pool-member actions or payouts
- Expected Immunefi impact: Bypass of wallet, daemon, keychain, RPC, pool, or Data Layer authorization that enables unauthorized signing, key use, coin control, payout redirection, singleton mutation, or protected state transitions
- Fast validation: toggle waiting-room and active-pool state around `chia/pools/pool_wallet.py:create_new_pool_wallet_transaction` and assert only canonical membership transitions succeed
