# Q3382: user-safe-mask via collateral-add: leave a residue that no reconciliation pass ever inspects

## Question
Entering through `collateral-add` (mainnet/contracts/market/v0-4-market.clar:1020) while controlling the `ft` trait principal, can an unprivileged attacker make `user-safe-mask` (mainnet/contracts/market/v0-4-market.clar:428) leave a residue that no reconciliation pass ever inspects? `user-safe-mask` ANDs the user's collateral bits against the enabled bitmap but keeps ALL debt bits unfiltered, so the invariant that shares outstanding valued at the current share price never exceed `total-assets` would fail, yielding direct theft of another user's collateral.

## Target
- File/function: `mainnet/contracts/market/v0-4-market.clar:428` -> `user-safe-mask`
- Entrypoint: `collateral-add` (`mainnet/contracts/market/v0-4-market.clar:1020`), unprivileged and publicly callable
- Attacker controls: the `ft` trait principal
- Exploit idea: `user-safe-mask` ANDs the user's collateral bits against the enabled bitmap but keeps ALL debt bits unfiltered. Reach it through `collateral-add` and leave a residue that no reconciliation pass ever inspects.
- Invariant to test: shares outstanding valued at the current share price never exceed `total-assets`
- Expected Immunefi impact: Critical - direct theft of another user's collateral
- Fast validation: Set up the position in simnet, call `collateral-add` with the `ft` trait principal, and assert on the printed event plus the post-state that collateral, debt and share totals still reconcile.
