# Q1200: oracle-last-update via collateral-remove-redeem: count one deposit as backing for two simultaneous claims

## Question
Does `collateral-remove-redeem` (mainnet/contracts/market/v0-4-market.clar:1211) let an unprivileged attacker who controls `amount` used for BOTH the collateral removal and the share redemption reach `oracle-last-update` (mainnet/contracts/market/v0-4-market.clar:939) in a state where it count one deposit as backing for two simultaneous claims? Given that it returns the stored monotonic timestamp for a `{type, ident}` key shared by every asset using that feed, the invariant that interest charged to borrowers equals interest distributed to suppliers plus treasury breaks and the result is permanent freezing of funds.

## Target
- File/function: `mainnet/contracts/market/v0-4-market.clar:939` -> `oracle-last-update`
- Entrypoint: `collateral-remove-redeem` (`mainnet/contracts/market/v0-4-market.clar:1211`), unprivileged and publicly callable
- Attacker controls: `amount` used for BOTH the collateral removal and the share redemption
- Exploit idea: `oracle-last-update` returns the stored monotonic timestamp for a `{type, ident}` key shared by every asset using that feed. Reach it through `collateral-remove-redeem` and count one deposit as backing for two simultaneous claims.
- Invariant to test: interest charged to borrowers equals interest distributed to suppliers plus treasury
- Expected Immunefi impact: Critical - permanent freezing of funds
- Fast validation: Fuzz `amount` used for BOTH the collateral removal and the share redemption across its boundary values through `collateral-remove-redeem` in simnet and assert `oracle-last-update` never returns a value that breaks the invariant.
