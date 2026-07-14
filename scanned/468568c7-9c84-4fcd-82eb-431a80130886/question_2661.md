# Q2661: select_coins accepts a spend path that diverges between validation stages

## Question
Can an unprivileged attacker reach wallet RPC or wallet sync flow reaching `select_coins` and control conflicting spend bundle fields, CLVM conditions, announcements, and fee/cost edge cases so that `PlotNFT2Wallet.select_coins` in `chia/wallet/plotnft_wallet/plotnft_wallet.py` executes a path where drive `select_coins` through two validation paths that should be equivalent, but make one path accept a spend bundle the other path rejects, violating the invariant that mempool admission, block validation, and wallet accounting must agree on whether the same spend is valid and leading to Consensus divergence, deterministic validation mismatch, invalid block or spend acceptance, forged weight proof trust, or chain halt caused by an unprivileged block, spend bundle, protocol message, sync path, or mempool interaction?

## Target
- File/function: chia/wallet/plotnft_wallet/plotnft_wallet.py:540 `PlotNFT2Wallet.select_coins`
- Entrypoint: wallet RPC or wallet sync flow reaching `select_coins`
- Attacker controls: conflicting spend bundle fields, CLVM conditions, announcements, and fee/cost edge cases
- Exploit idea: drive `select_coins` through two validation paths that should be equivalent, but make one path accept a spend bundle the other path rejects
- Invariant to test: mempool admission, block validation, and wallet accounting must agree on whether the same spend is valid
- Expected Immunefi impact: Consensus divergence, deterministic validation mismatch, invalid block or spend acceptance, forged weight proof trust, or chain halt caused by an unprivileged block, spend bundle, protocol message, sync path, or mempool interaction
- Fast validation: unit-test `chia/wallet/plotnft_wallet/plotnft_wallet.py:select_coins` with paired spend bundles that differ only in one edge-condition and assert mempool acceptance equals block acceptance
