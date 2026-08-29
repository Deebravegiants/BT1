# Q1504: mask-pos via collateral-add: count one deposit as backing for two simultaneous claims

## Question
Does `collateral-add` (mainnet/contracts/market/v0-4-market.clar:1020) let an unprivileged attacker who controls whether this asset is already collateral (the is-new-collateral branch) reach `mask-pos` (mainnet/contracts/market/v0-market-vault.clar:91) in a state where it count one deposit as backing for two simultaneous claims? Given that it maps an asset id to a bit position, offsetting debt bits by DEBT-OFFSET, the invariant that interest charged to borrowers equals interest distributed to suppliers plus treasury breaks and the result is direct theft of user funds at rest or in motion.

## Target
- File/function: `mainnet/contracts/market/v0-market-vault.clar:91` -> `mask-pos`
- Entrypoint: `collateral-add` (`mainnet/contracts/market/v0-4-market.clar:1020`), unprivileged and publicly callable
- Attacker controls: whether this asset is already collateral (the is-new-collateral branch)
- Exploit idea: `mask-pos` maps an asset id to a bit position, offsetting debt bits by DEBT-OFFSET. Reach it through `collateral-add` and count one deposit as backing for two simultaneous claims.
- Invariant to test: interest charged to borrowers equals interest distributed to suppliers plus treasury
- Expected Immunefi impact: Critical - direct theft of user funds at rest or in motion
- Fast validation: Set up the position in simnet, call `collateral-add` with whether this asset is already collateral (the is-new-collateral branch), and assert on the printed event plus the post-state that collateral, debt and share totals still reconcile.
