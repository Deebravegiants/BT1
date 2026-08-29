# Q5029: linear-interpolate via deposit: leave a residue that no reconciliation pass ever inspects

## Question
Can an unprivileged attacker entering through `deposit` (mainnet/contracts/vault/v0-vault-stx.clar:763), controlling the vault's supply and asset state at the moment of the call, drive `linear-interpolate` (mainnet/contracts/vault/v0-vault-stx.clar:221) — which interpolates between two points, dividing by `(- x2 x1)` — to leave a residue that no reconciliation pass ever inspects, breaking the invariant that tokens held by .v0-market-vault equal the sum of its `collateral` map for that asset, and cause theft of unclaimed yield?

## Target
- File/function: `mainnet/contracts/vault/v0-vault-stx.clar:221` -> `linear-interpolate`
- Entrypoint: `deposit` (`mainnet/contracts/vault/v0-vault-stx.clar:763`), unprivileged and publicly callable
- Attacker controls: the vault's supply and asset state at the moment of the call
- Exploit idea: `linear-interpolate` interpolates between two points, dividing by `(- x2 x1)`. Reach it through `deposit` and leave a residue that no reconciliation pass ever inspects.
- Invariant to test: tokens held by .v0-market-vault equal the sum of its `collateral` map for that asset
- Expected Immunefi impact: High - theft of unclaimed yield
- Fast validation: In `local-testing/tests` on a local fork, drive `deposit` with the vault's supply and asset state at the moment of the call, then read `linear-interpolate` state before and after in the same block and assert the two sides of the invariant are equal.
