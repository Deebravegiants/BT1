# Q4666: oracle-last-update via collateral-add: destroy value through a truncation the opposite operation 

## Question
Entering through `collateral-add` (mainnet/contracts/market/v0-4-market.clar:1020) while controlling `amount`, can an unprivileged attacker make `oracle-last-update` (mainnet/contracts/market/v0-4-market.clar:939) destroy value through a truncation the opposite operation does not restore? `oracle-last-update` returns the stored monotonic timestamp for a `{type, ident}` key shared by every asset using that feed, so the invariant that `principal-scaled` and `total-borrowed` describe the same outstanding principal would fail, yielding direct theft of another user's collateral.

## Target
- File/function: `mainnet/contracts/market/v0-4-market.clar:939` -> `oracle-last-update`
- Entrypoint: `collateral-add` (`mainnet/contracts/market/v0-4-market.clar:1020`), unprivileged and publicly callable
- Attacker controls: `amount`
- Exploit idea: `oracle-last-update` returns the stored monotonic timestamp for a `{type, ident}` key shared by every asset using that feed. Reach it through `collateral-add` and destroy value through a truncation the opposite operation does not restore.
- Invariant to test: `principal-scaled` and `total-borrowed` describe the same outstanding principal
- Expected Immunefi impact: Critical - direct theft of another user's collateral
- Fast validation: Set up the position in simnet, call `collateral-add` with `amount`, and assert on the printed event plus the post-state that collateral, debt and share totals still reconcile.
