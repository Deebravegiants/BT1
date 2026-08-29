# Q3658: calc-liq-factor via liquidate-multi: leave a residue that no reconciliation pass ever inspects

## Question
Entering through `liquidate-multi` (mainnet/contracts/market/v0-4-market.clar:1593) while controlling the full batch list and its ordering, can an unprivileged attacker make `calc-liq-factor` (mainnet/contracts/market/v0-4-market.clar:703) leave a residue that no reconciliation pass ever inspects? `calc-liq-factor` computes `(- ltv-curr ltv-liq-partial)` over `(- ltv-liq-full ltv-liq-partial)`, a subtraction that aborts below the partial threshold, so the invariant that interest charged to borrowers equals interest distributed to suppliers plus treasury would fail, yielding direct theft of another user's collateral.

## Target
- File/function: `mainnet/contracts/market/v0-4-market.clar:703` -> `calc-liq-factor`
- Entrypoint: `liquidate-multi` (`mainnet/contracts/market/v0-4-market.clar:1593`), unprivileged and publicly callable
- Attacker controls: the full batch list and its ordering
- Exploit idea: `calc-liq-factor` computes `(- ltv-curr ltv-liq-partial)` over `(- ltv-liq-full ltv-liq-partial)`, a subtraction that aborts below the partial threshold. Reach it through `liquidate-multi` and leave a residue that no reconciliation pass ever inspects.
- Invariant to test: interest charged to borrowers equals interest distributed to suppliers plus treasury
- Expected Immunefi impact: Critical - direct theft of another user's collateral
- Fast validation: Set up the position in simnet, call `liquidate-multi` with the full batch list and its ordering, and assert on the printed event plus the post-state that collateral, debt and share totals still reconcile.
