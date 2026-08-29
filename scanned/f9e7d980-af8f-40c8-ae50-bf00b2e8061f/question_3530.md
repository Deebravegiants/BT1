# Q3530: iter-price-multi via liquidate-multi: leave a residue that no reconciliation pass ever inspects

## Question
Entering through `liquidate-multi` (mainnet/contracts/market/v0-4-market.clar:1593) while controlling the full batch list and its ordering, can an unprivileged attacker make `iter-price-multi` (mainnet/contracts/market/v0-4-market.clar:405) leave a residue that no reconciliation pass ever inspects? `iter-price-multi` carries `aids` and `idx` in its accumulator but never uses them to align prices with asset ids, and appends under `as-max-len? ... u64`, so the invariant that interest charged to borrowers equals interest distributed to suppliers plus treasury would fail, yielding protocol insolvency.

## Target
- File/function: `mainnet/contracts/market/v0-4-market.clar:405` -> `iter-price-multi`
- Entrypoint: `liquidate-multi` (`mainnet/contracts/market/v0-4-market.clar:1593`), unprivileged and publicly callable
- Attacker controls: the full batch list and its ordering
- Exploit idea: `iter-price-multi` carries `aids` and `idx` in its accumulator but never uses them to align prices with asset ids, and appends under `as-max-len? ... u64`. Reach it through `liquidate-multi` and leave a residue that no reconciliation pass ever inspects.
- Invariant to test: interest charged to borrowers equals interest distributed to suppliers plus treasury
- Expected Immunefi impact: Critical - protocol insolvency
- Fast validation: Write a Clarinet simnet test calling `liquidate-multi` twice with the full batch list and its ordering varied, and assert that the value `iter-price-multi` returns is identical in both runs; a divergence confirms the finding.
