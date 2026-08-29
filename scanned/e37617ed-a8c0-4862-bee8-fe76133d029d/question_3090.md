# Q3090: filter-out-debt-asset via liquidate-multi: leave a residue that no reconciliation pass ever inspects

## Question
Entering through `liquidate-multi` (mainnet/contracts/market/v0-4-market.clar:1593) while controlling the full batch list and its ordering, can an unprivileged attacker make `filter-out-debt-asset` (mainnet/contracts/market/v0-4-market.clar:633) leave a residue that no reconciliation pass ever inspects? `filter-out-debt-asset` rebuilds the debt list without one asset, under `as-max-len? ... u64`, so the invariant that interest charged to borrowers equals interest distributed to suppliers plus treasury would fail, yielding permanent freezing of funds.

## Target
- File/function: `mainnet/contracts/market/v0-4-market.clar:633` -> `filter-out-debt-asset`
- Entrypoint: `liquidate-multi` (`mainnet/contracts/market/v0-4-market.clar:1593`), unprivileged and publicly callable
- Attacker controls: the full batch list and its ordering
- Exploit idea: `filter-out-debt-asset` rebuilds the debt list without one asset, under `as-max-len? ... u64`. Reach it through `liquidate-multi` and leave a residue that no reconciliation pass ever inspects.
- Invariant to test: interest charged to borrowers equals interest distributed to suppliers plus treasury
- Expected Immunefi impact: Critical - permanent freezing of funds
- Fast validation: Fuzz the full batch list and its ordering across its boundary values through `liquidate-multi` in simnet and assert `filter-out-debt-asset` never returns a value that breaks the invariant.
