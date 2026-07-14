# Q2607: join_pool accepts a pool membership transition with stale or swapped state

## Question
Can an unprivileged attacker reach wallet RPC or wallet sync flow reaching `join_pool` and control launcher ids, pool target state, delayed puzzle data, and join/leave sequencing so that `PlotNFT2Wallet.join_pool` in `chia/wallet/plotnft_wallet/plotnft_wallet.py` executes a path where make `join_pool` apply pool join, leave, or waiting-room state under swapped singleton context, violating the invariant that pool membership state must advance only through canonical singleton transitions and leading to Bypass of wallet, daemon, keychain, RPC, pool, or Data Layer authorization that enables unauthorized signing, key use, coin control, payout redirection, singleton mutation, or protected state transitions?

## Target
- File/function: chia/wallet/plotnft_wallet/plotnft_wallet.py:216 `PlotNFT2Wallet.join_pool`
- Entrypoint: wallet RPC or wallet sync flow reaching `join_pool`
- Attacker controls: launcher ids, pool target state, delayed puzzle data, and join/leave sequencing
- Exploit idea: make `join_pool` apply pool join, leave, or waiting-room state under swapped singleton context
- Invariant to test: pool membership state must advance only through canonical singleton transitions
- Expected Immunefi impact: Bypass of wallet, daemon, keychain, RPC, pool, or Data Layer authorization that enables unauthorized signing, key use, coin control, payout redirection, singleton mutation, or protected state transitions
- Fast validation: drive join/leave transitions with stale singleton context into `chia/wallet/plotnft_wallet/plotnft_wallet.py:join_pool` and assert state changes reject cleanly
