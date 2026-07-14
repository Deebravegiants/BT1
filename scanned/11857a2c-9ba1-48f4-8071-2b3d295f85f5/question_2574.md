# Q2574: add_pool_reward accepts a pool membership transition with stale or swapped state

## Question
Can an unprivileged attacker reach wallet RPC or wallet sync flow reaching `add_pool_reward` and control launcher ids, pool target state, delayed puzzle data, and join/leave sequencing so that `PlotNFTStore.add_pool_reward` in `chia/wallet/plotnft_wallet/plotnft_store.py` executes a path where make `add_pool_reward` apply pool join, leave, or waiting-room state under swapped singleton context, violating the invariant that pool membership state must advance only through canonical singleton transitions and leading to Bypass of wallet, daemon, keychain, RPC, pool, or Data Layer authorization that enables unauthorized signing, key use, coin control, payout redirection, singleton mutation, or protected state transitions?

## Target
- File/function: chia/wallet/plotnft_wallet/plotnft_store.py:113 `PlotNFTStore.add_pool_reward`
- Entrypoint: wallet RPC or wallet sync flow reaching `add_pool_reward`
- Attacker controls: launcher ids, pool target state, delayed puzzle data, and join/leave sequencing
- Exploit idea: make `add_pool_reward` apply pool join, leave, or waiting-room state under swapped singleton context
- Invariant to test: pool membership state must advance only through canonical singleton transitions
- Expected Immunefi impact: Bypass of wallet, daemon, keychain, RPC, pool, or Data Layer authorization that enables unauthorized signing, key use, coin control, payout redirection, singleton mutation, or protected state transitions
- Fast validation: drive join/leave transitions with stale singleton context into `chia/wallet/plotnft_wallet/plotnft_store.py:add_pool_reward` and assert state changes reject cleanly
