# Q2954: iter-find-superset via liquidate: leave a residue that no reconciliation pass ever inspects

## Question
Entering through `liquidate` (mainnet/contracts/market/v0-4-market.clar:1382) while controlling which collateral and debt asset pair is targeted, can an unprivileged attacker make `iter-find-superset` (mainnet/contracts/registry/v0-egroup.clar:267) leave a residue that no reconciliation pass ever inspects? `iter-find-superset` short-circuits on the first superset match, so the invariant that interest charged to borrowers equals interest distributed to suppliers plus treasury would fail, yielding protocol insolvency.

## Target
- File/function: `mainnet/contracts/registry/v0-egroup.clar:267` -> `iter-find-superset`
- Entrypoint: `liquidate` (`mainnet/contracts/market/v0-4-market.clar:1382`), unprivileged and publicly callable
- Attacker controls: which collateral and debt asset pair is targeted
- Exploit idea: `iter-find-superset` short-circuits on the first superset match. Reach it through `liquidate` and leave a residue that no reconciliation pass ever inspects.
- Invariant to test: interest charged to borrowers equals interest distributed to suppliers plus treasury
- Expected Immunefi impact: Critical - protocol insolvency
- Fast validation: Write a Clarinet simnet test calling `liquidate` twice with which collateral and debt asset pair is targeted varied, and assert that the value `iter-find-superset` returns is identical in both runs; a divergence confirms the finding.
