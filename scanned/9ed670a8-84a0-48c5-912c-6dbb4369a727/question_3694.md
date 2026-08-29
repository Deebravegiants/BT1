# Q3694: accrue-debt-asset via collateral-add: leave a residue that no reconciliation pass ever inspects

## Question
Entering through `collateral-add` (mainnet/contracts/market/v0-4-market.clar:1020) while controlling the `ft` trait principal, can an unprivileged attacker make `accrue-debt-asset` (mainnet/contracts/market/v0-4-market.clar:262) leave a residue that no reconciliation pass ever inspects? `accrue-debt-asset` calls `accrue-and-cache` with `unwrap-panic` inside a fold whose accumulator ignores the result, so the invariant that shares outstanding valued at the current share price never exceed `total-assets` would fail, yielding direct theft of another user's collateral.

## Target
- File/function: `mainnet/contracts/market/v0-4-market.clar:262` -> `accrue-debt-asset`
- Entrypoint: `collateral-add` (`mainnet/contracts/market/v0-4-market.clar:1020`), unprivileged and publicly callable
- Attacker controls: the `ft` trait principal
- Exploit idea: `accrue-debt-asset` calls `accrue-and-cache` with `unwrap-panic` inside a fold whose accumulator ignores the result. Reach it through `collateral-add` and leave a residue that no reconciliation pass ever inspects.
- Invariant to test: shares outstanding valued at the current share price never exceed `total-assets`
- Expected Immunefi impact: Critical - direct theft of another user's collateral
- Fast validation: Set up the position in simnet, call `collateral-add` with the `ft` trait principal, and assert on the printed event plus the post-state that collateral, debt and share totals still reconcile.
