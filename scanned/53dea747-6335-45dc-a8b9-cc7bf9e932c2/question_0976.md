# Q0976: calc-cumulative-debt via collateral-remove-redeem: destroy value through a truncation the opposite operation 

## Question
Does `collateral-remove-redeem` (mainnet/contracts/market/v0-4-market.clar:1211) let an unprivileged attacker who controls `amount` used for BOTH the collateral removal and the share redemption reach `calc-cumulative-debt` (mainnet/contracts/vault/v0-vault-stx.clar:180) in a state where it destroy value through a truncation the opposite operation does not restore? Given that it multiplies scaled principal by an index, the invariant that every round-up has a paired round-down that repetition cannot exploit breaks and the result is direct theft of another user's collateral.

## Target
- File/function: `mainnet/contracts/vault/v0-vault-stx.clar:180` -> `calc-cumulative-debt`
- Entrypoint: `collateral-remove-redeem` (`mainnet/contracts/market/v0-4-market.clar:1211`), unprivileged and publicly callable
- Attacker controls: `amount` used for BOTH the collateral removal and the share redemption
- Exploit idea: `calc-cumulative-debt` multiplies scaled principal by an index. Reach it through `collateral-remove-redeem` and destroy value through a truncation the opposite operation does not restore.
- Invariant to test: every round-up has a paired round-down that repetition cannot exploit
- Expected Immunefi impact: Critical - direct theft of another user's collateral
- Fast validation: Set up the position in simnet, call `collateral-remove-redeem` with `amount` used for BOTH the collateral removal and the share redemption, and assert on the printed event plus the post-state that collateral, debt and share totals still reconcile.
