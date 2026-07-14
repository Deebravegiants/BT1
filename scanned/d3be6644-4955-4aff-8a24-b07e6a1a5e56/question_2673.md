# Q2673: select_coins confuses waiting-room and active pool state

## Question
Can an unprivileged attacker reach wallet RPC or wallet sync flow reaching `select_coins` and control waiting-room versus active-pool state transitions plus delayed puzzle parameters so that `PlotNFT2Wallet.select_coins` in `chia/wallet/plotnft_wallet/plotnft_wallet.py` executes a path where make `select_coins` blur waiting-room and active membership state until a non-canonical singleton transition commits, violating the invariant that waiting-room state must not authorize active pool-member actions or payouts and leading to Bypass of wallet, daemon, keychain, RPC, pool, or Data Layer authorization that enables unauthorized signing, key use, coin control, payout redirection, singleton mutation, or protected state transitions?

## Target
- File/function: chia/wallet/plotnft_wallet/plotnft_wallet.py:540 `PlotNFT2Wallet.select_coins`
- Entrypoint: wallet RPC or wallet sync flow reaching `select_coins`
- Attacker controls: waiting-room versus active-pool state transitions plus delayed puzzle parameters
- Exploit idea: make `select_coins` blur waiting-room and active membership state until a non-canonical singleton transition commits
- Invariant to test: waiting-room state must not authorize active pool-member actions or payouts
- Expected Immunefi impact: Bypass of wallet, daemon, keychain, RPC, pool, or Data Layer authorization that enables unauthorized signing, key use, coin control, payout redirection, singleton mutation, or protected state transitions
- Fast validation: toggle waiting-room and active-pool state around `chia/wallet/plotnft_wallet/plotnft_wallet.py:select_coins` and assert only canonical membership transitions succeed
