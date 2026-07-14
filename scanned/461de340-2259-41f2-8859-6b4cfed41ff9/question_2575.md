# Q2575: add_pool_reward confuses waiting-room and active pool state

## Question
Can an unprivileged attacker reach wallet RPC or wallet sync flow reaching `add_pool_reward` and control waiting-room versus active-pool state transitions plus delayed puzzle parameters so that `PlotNFTStore.add_pool_reward` in `chia/wallet/plotnft_wallet/plotnft_store.py` executes a path where make `add_pool_reward` blur waiting-room and active membership state until a non-canonical singleton transition commits, violating the invariant that waiting-room state must not authorize active pool-member actions or payouts and leading to Bypass of wallet, daemon, keychain, RPC, pool, or Data Layer authorization that enables unauthorized signing, key use, coin control, payout redirection, singleton mutation, or protected state transitions?

## Target
- File/function: chia/wallet/plotnft_wallet/plotnft_store.py:113 `PlotNFTStore.add_pool_reward`
- Entrypoint: wallet RPC or wallet sync flow reaching `add_pool_reward`
- Attacker controls: waiting-room versus active-pool state transitions plus delayed puzzle parameters
- Exploit idea: make `add_pool_reward` blur waiting-room and active membership state until a non-canonical singleton transition commits
- Invariant to test: waiting-room state must not authorize active pool-member actions or payouts
- Expected Immunefi impact: Bypass of wallet, daemon, keychain, RPC, pool, or Data Layer authorization that enables unauthorized signing, key use, coin control, payout redirection, singleton mutation, or protected state transitions
- Fast validation: toggle waiting-room and active-pool state around `chia/wallet/plotnft_wallet/plotnft_store.py:add_pool_reward` and assert only canonical membership transitions succeed
