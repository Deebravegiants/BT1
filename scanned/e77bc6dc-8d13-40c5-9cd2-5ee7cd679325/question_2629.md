# Q2629: coin_added confuses waiting-room and active pool state

## Question
Can an unprivileged attacker reach wallet RPC or wallet sync flow reaching `coin_added` and control waiting-room versus active-pool state transitions plus delayed puzzle parameters so that `PlotNFT2Wallet.coin_added` in `chia/wallet/plotnft_wallet/plotnft_wallet.py` executes a path where make `coin_added` blur waiting-room and active membership state until a non-canonical singleton transition commits, violating the invariant that waiting-room state must not authorize active pool-member actions or payouts and leading to Bypass of wallet, daemon, keychain, RPC, pool, or Data Layer authorization that enables unauthorized signing, key use, coin control, payout redirection, singleton mutation, or protected state transitions?

## Target
- File/function: chia/wallet/plotnft_wallet/plotnft_wallet.py:410 `PlotNFT2Wallet.coin_added`
- Entrypoint: wallet RPC or wallet sync flow reaching `coin_added`
- Attacker controls: waiting-room versus active-pool state transitions plus delayed puzzle parameters
- Exploit idea: make `coin_added` blur waiting-room and active membership state until a non-canonical singleton transition commits
- Invariant to test: waiting-room state must not authorize active pool-member actions or payouts
- Expected Immunefi impact: Bypass of wallet, daemon, keychain, RPC, pool, or Data Layer authorization that enables unauthorized signing, key use, coin control, payout redirection, singleton mutation, or protected state transitions
- Fast validation: toggle waiting-room and active-pool state around `chia/wallet/plotnft_wallet/plotnft_wallet.py:coin_added` and assert only canonical membership transitions succeed
