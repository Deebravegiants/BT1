# Q3290: mask-to-list-iter via repay: leave a residue that no reconciliation pass ever inspects

## Question
Entering through `repay` (mainnet/contracts/market/v0-4-market.clar:1316) while controlling `amount`, including far above the real debt (the capping path), can an unprivileged attacker make `mask-to-list-iter` (mainnet/contracts/market/v0-4-market.clar:440) leave a residue that no reconciliation pass ever inspects? `mask-to-list-iter` appends under `(unwrap-panic (as-max-len? ... u64))`, aborting if the position exceeds the bound, so the invariant that interest charged to borrowers equals interest distributed to suppliers plus treasury would fail, yielding protocol insolvency through uncollateralised debt.

## Target
- File/function: `mainnet/contracts/market/v0-4-market.clar:440` -> `mask-to-list-iter`
- Entrypoint: `repay` (`mainnet/contracts/market/v0-4-market.clar:1316`), unprivileged and publicly callable
- Attacker controls: `amount`, including far above the real debt (the capping path)
- Exploit idea: `mask-to-list-iter` appends under `(unwrap-panic (as-max-len? ... u64))`, aborting if the position exceeds the bound. Reach it through `repay` and leave a residue that no reconciliation pass ever inspects.
- Invariant to test: interest charged to borrowers equals interest distributed to suppliers plus treasury
- Expected Immunefi impact: Critical - protocol insolvency through uncollateralised debt
- Fast validation: Write a Clarinet simnet test calling `repay` twice with `amount`, including far above the real debt (the capping path) varied, and assert that the value `mask-to-list-iter` returns is identical in both runs; a divergence confirms the finding.
