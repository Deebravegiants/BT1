# Q1080: resolve-price-feed via collateral-remove: count one deposit as backing for two simultaneous claims

## Question
Does `collateral-remove` (mainnet/contracts/market/v0-4-market.clar:1107) let an unprivileged attacker who controls `amount` relative to the current collateral row (the removing-all branch) reach `resolve-price-feed` (mainnet/contracts/market/v0-4-market.clar:332) in a state where it count one deposit as backing for two simultaneous claims? Given that it dispatches on a 1-byte type to `resolve-pyth` or `resolve-dia`, erroring otherwise, the invariant that interest charged to borrowers equals interest distributed to suppliers plus treasury breaks and the result is temporary freezing of funds.

## Target
- File/function: `mainnet/contracts/market/v0-4-market.clar:332` -> `resolve-price-feed`
- Entrypoint: `collateral-remove` (`mainnet/contracts/market/v0-4-market.clar:1107`), unprivileged and publicly callable
- Attacker controls: `amount` relative to the current collateral row (the removing-all branch)
- Exploit idea: `resolve-price-feed` dispatches on a 1-byte type to `resolve-pyth` or `resolve-dia`, erroring otherwise. Reach it through `collateral-remove` and count one deposit as backing for two simultaneous claims.
- Invariant to test: interest charged to borrowers equals interest distributed to suppliers plus treasury
- Expected Immunefi impact: High - temporary freezing of funds
- Fast validation: Fuzz `amount` relative to the current collateral row (the removing-all branch) across its boundary values through `collateral-remove` in simnet and assert `resolve-price-feed` never returns a value that breaks the invariant.
