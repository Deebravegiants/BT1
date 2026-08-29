# Q3250: price-multi-resolve via borrow: leave a residue that no reconciliation pass ever inspects

## Question
Entering through `borrow` (mainnet/contracts/market/v0-4-market.clar:1238) while controlling `amount`, can an unprivileged attacker make `price-multi-resolve` (mainnet/contracts/market/v0-4-market.clar:397) leave a residue that no reconciliation pass ever inspects? `price-multi-resolve` folds `iter-price-multi` into a POSITIONAL price list, asserting only the `valid` flag at the end, so the invariant that interest charged to borrowers equals interest distributed to suppliers plus treasury would fail, yielding direct theft of user funds at rest or in motion.

## Target
- File/function: `mainnet/contracts/market/v0-4-market.clar:397` -> `price-multi-resolve`
- Entrypoint: `borrow` (`mainnet/contracts/market/v0-4-market.clar:1238`), unprivileged and publicly callable
- Attacker controls: `amount`
- Exploit idea: `price-multi-resolve` folds `iter-price-multi` into a POSITIONAL price list, asserting only the `valid` flag at the end. Reach it through `borrow` and leave a residue that no reconciliation pass ever inspects.
- Invariant to test: interest charged to borrowers equals interest distributed to suppliers plus treasury
- Expected Immunefi impact: Critical - direct theft of user funds at rest or in motion
- Fast validation: Set up the position in simnet, call `borrow` with `amount`, and assert on the printed event plus the post-state that collateral, debt and share totals still reconcile.
