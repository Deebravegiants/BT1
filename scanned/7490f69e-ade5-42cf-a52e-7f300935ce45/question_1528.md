# Q1528: add-user-collateral via collateral-remove-redeem: count one deposit as backing for two simultaneous claims

## Question
Does `collateral-remove-redeem` (mainnet/contracts/market/v0-4-market.clar:1211) let an unprivileged attacker who controls the zToken/underlying id mapping reached (the u100 sentinel branch) reach `add-user-collateral` (mainnet/contracts/market/v0-market-vault.clar:198) in a state where it count one deposit as backing for two simultaneous claims? Given that it adds to the collateral row with a graceful u0 default, the invariant that interest charged to borrowers equals interest distributed to suppliers plus treasury breaks and the result is theft of unclaimed yield.

## Target
- File/function: `mainnet/contracts/market/v0-market-vault.clar:198` -> `add-user-collateral`
- Entrypoint: `collateral-remove-redeem` (`mainnet/contracts/market/v0-4-market.clar:1211`), unprivileged and publicly callable
- Attacker controls: the zToken/underlying id mapping reached (the u100 sentinel branch)
- Exploit idea: `add-user-collateral` adds to the collateral row with a graceful u0 default. Reach it through `collateral-remove-redeem` and count one deposit as backing for two simultaneous claims.
- Invariant to test: interest charged to borrowers equals interest distributed to suppliers plus treasury
- Expected Immunefi impact: High - theft of unclaimed yield
- Fast validation: Set up the position in simnet, call `collateral-remove-redeem` with the zToken/underlying id mapping reached (the u100 sentinel branch), and assert on the printed event plus the post-state that collateral, debt and share totals still reconcile.
