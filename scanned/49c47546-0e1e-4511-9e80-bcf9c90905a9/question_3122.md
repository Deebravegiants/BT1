# Q3122: filter-out-debt-asset via collateral-remove: leave a residue that no reconciliation pass ever inspects

## Question
Entering through `collateral-remove` (mainnet/contracts/market/v0-4-market.clar:1107) while controlling the `price-feeds` buffers, can an unprivileged attacker make `filter-out-debt-asset` (mainnet/contracts/market/v0-4-market.clar:633) leave a residue that no reconciliation pass ever inspects? `filter-out-debt-asset` rebuilds the debt list without one asset, under `as-max-len? ... u64`, so the invariant that interest charged to borrowers equals interest distributed to suppliers plus treasury would fail, yielding protocol insolvency.

## Target
- File/function: `mainnet/contracts/market/v0-4-market.clar:633` -> `filter-out-debt-asset`
- Entrypoint: `collateral-remove` (`mainnet/contracts/market/v0-4-market.clar:1107`), unprivileged and publicly callable
- Attacker controls: the `price-feeds` buffers
- Exploit idea: `filter-out-debt-asset` rebuilds the debt list without one asset, under `as-max-len? ... u64`. Reach it through `collateral-remove` and leave a residue that no reconciliation pass ever inspects.
- Invariant to test: interest charged to borrowers equals interest distributed to suppliers plus treasury
- Expected Immunefi impact: Critical - protocol insolvency
- Fast validation: Write a Clarinet simnet test calling `collateral-remove` twice with the `price-feeds` buffers varied, and assert that the value `filter-out-debt-asset` returns is identical in both runs; a divergence confirms the finding.
