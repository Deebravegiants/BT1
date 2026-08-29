# Q3598: check-confidence via collateral-remove-redeem: leave a residue that no reconciliation pass ever inspects

## Question
Entering through `collateral-remove-redeem` (mainnet/contracts/market/v0-4-market.clar:1211) while controlling `amount` used for BOTH the collateral removal and the share redemption, can an unprivileged attacker make `check-confidence` (mainnet/contracts/market/v0-4-market.clar:305) leave a residue that no reconciliation pass ever inspects? `check-confidence` compares the Pyth confidence interval against `max-confidence-ratio` in BPS, a gate that has no DIA equivalent, so the invariant that shares outstanding valued at the current share price never exceed `total-assets` would fail, yielding theft of unclaimed yield.

## Target
- File/function: `mainnet/contracts/market/v0-4-market.clar:305` -> `check-confidence`
- Entrypoint: `collateral-remove-redeem` (`mainnet/contracts/market/v0-4-market.clar:1211`), unprivileged and publicly callable
- Attacker controls: `amount` used for BOTH the collateral removal and the share redemption
- Exploit idea: `check-confidence` compares the Pyth confidence interval against `max-confidence-ratio` in BPS, a gate that has no DIA equivalent. Reach it through `collateral-remove-redeem` and leave a residue that no reconciliation pass ever inspects.
- Invariant to test: shares outstanding valued at the current share price never exceed `total-assets`
- Expected Immunefi impact: High - theft of unclaimed yield
- Fast validation: Set up the position in simnet, call `collateral-remove-redeem` with `amount` used for BOTH the collateral removal and the share redemption, and assert on the printed event plus the post-state that collateral, debt and share totals still reconcile.
