# Q2628: coin_added accepts a pool membership transition with stale or swapped state

## Question
Can an unprivileged attacker reach wallet RPC or wallet sync flow reaching `coin_added` and control launcher ids, pool target state, delayed puzzle data, and join/leave sequencing so that `PlotNFT2Wallet.coin_added` in `chia/wallet/plotnft_wallet/plotnft_wallet.py` executes a path where make `coin_added` apply pool join, leave, or waiting-room state under swapped singleton context, violating the invariant that pool membership state must advance only through canonical singleton transitions and leading to Bypass of wallet, daemon, keychain, RPC, pool, or Data Layer authorization that enables unauthorized signing, key use, coin control, payout redirection, singleton mutation, or protected state transitions?

## Target
- File/function: chia/wallet/plotnft_wallet/plotnft_wallet.py:410 `PlotNFT2Wallet.coin_added`
- Entrypoint: wallet RPC or wallet sync flow reaching `coin_added`
- Attacker controls: launcher ids, pool target state, delayed puzzle data, and join/leave sequencing
- Exploit idea: make `coin_added` apply pool join, leave, or waiting-room state under swapped singleton context
- Invariant to test: pool membership state must advance only through canonical singleton transitions
- Expected Immunefi impact: Bypass of wallet, daemon, keychain, RPC, pool, or Data Layer authorization that enables unauthorized signing, key use, coin control, payout redirection, singleton mutation, or protected state transitions
- Fast validation: drive join/leave transitions with stale singleton context into `chia/wallet/plotnft_wallet/plotnft_wallet.py:coin_added` and assert state changes reject cleanly
