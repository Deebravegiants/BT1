# Q2974: total-supply-preview via supply-collateral-add: leave a residue that no reconciliation pass ever inspects

## Question
Entering through `supply-collateral-add` (mainnet/contracts/market/v0-4-market.clar:1175) while controlling `min-shares` (the only slippage bound on the deposit leg), can an unprivileged attacker make `total-supply-preview` (mainnet/contracts/vault/v0-vault-stx.clar:363) leave a residue that no reconciliation pass ever inspects? `total-supply-preview` adds the not-yet-minted `calc-treasury-lp-preview` to the live supply that both conversions price against, so the invariant that shares outstanding valued at the current share price never exceed `total-assets` would fail, yielding direct theft of another user's collateral.

## Target
- File/function: `mainnet/contracts/vault/v0-vault-stx.clar:363` -> `total-supply-preview`
- Entrypoint: `supply-collateral-add` (`mainnet/contracts/market/v0-4-market.clar:1175`), unprivileged and publicly callable
- Attacker controls: `min-shares` (the only slippage bound on the deposit leg)
- Exploit idea: `total-supply-preview` adds the not-yet-minted `calc-treasury-lp-preview` to the live supply that both conversions price against. Reach it through `supply-collateral-add` and leave a residue that no reconciliation pass ever inspects.
- Invariant to test: shares outstanding valued at the current share price never exceed `total-assets`
- Expected Immunefi impact: Critical - direct theft of another user's collateral
- Fast validation: Set up the position in simnet, call `supply-collateral-add` with `min-shares` (the only slippage bound on the deposit leg), and assert on the printed event plus the post-state that collateral, debt and share totals still reconcile.
