# Q3650: unwrap-status via borrow: leave a residue that no reconciliation pass ever inspects

## Question
Entering through `borrow` (mainnet/contracts/market/v0-4-market.clar:1238) while controlling the future mask produced by the new debt bit, can an unprivileged attacker make `unwrap-status` (mainnet/contracts/registry/v0-assets.clar:111) leave a residue that no reconciliation pass ever inspects? `unwrap-status` resolves `status` with `unwrap-panic`, so the invariant that interest charged to borrowers equals interest distributed to suppliers plus treasury would fail, yielding protocol insolvency through uncollateralised debt.

## Target
- File/function: `mainnet/contracts/registry/v0-assets.clar:111` -> `unwrap-status`
- Entrypoint: `borrow` (`mainnet/contracts/market/v0-4-market.clar:1238`), unprivileged and publicly callable
- Attacker controls: the future mask produced by the new debt bit
- Exploit idea: `unwrap-status` resolves `status` with `unwrap-panic`. Reach it through `borrow` and leave a residue that no reconciliation pass ever inspects.
- Invariant to test: interest charged to borrowers equals interest distributed to suppliers plus treasury
- Expected Immunefi impact: Critical - protocol insolvency through uncollateralised debt
- Fast validation: Write a Clarinet simnet test calling `borrow` twice with the future mask produced by the new debt bit varied, and assert that the value `unwrap-status` returns is identical in both runs; a divergence confirms the finding.
