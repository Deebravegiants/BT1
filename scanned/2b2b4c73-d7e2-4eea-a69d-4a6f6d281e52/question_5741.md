# Q5741: mask-pos via supply-collateral-add: leave a residue that no reconciliation pass ever inspects

## Question
Can an unprivileged attacker entering through `supply-collateral-add` (mainnet/contracts/market/v0-4-market.clar:1175), controlling `amount`, drive `mask-pos` (mainnet/contracts/market/v0-market-vault.clar:91) — which maps an asset id to a bit position, offsetting debt bits by DEBT-OFFSET — to leave a residue that no reconciliation pass ever inspects, breaking the invariant that tokens held by .v0-market-vault equal the sum of its `collateral` map for that asset, and cause protocol insolvency through uncollateralised debt?

## Target
- File/function: `mainnet/contracts/market/v0-market-vault.clar:91` -> `mask-pos`
- Entrypoint: `supply-collateral-add` (`mainnet/contracts/market/v0-4-market.clar:1175`), unprivileged and publicly callable
- Attacker controls: `amount`
- Exploit idea: `mask-pos` maps an asset id to a bit position, offsetting debt bits by DEBT-OFFSET. Reach it through `supply-collateral-add` and leave a residue that no reconciliation pass ever inspects.
- Invariant to test: tokens held by .v0-market-vault equal the sum of its `collateral` map for that asset
- Expected Immunefi impact: Critical - protocol insolvency through uncollateralised debt
- Fast validation: Run the baseline `supply-collateral-add` call, then the attacker-shaped one with `amount`, and assert the attacker's net token balance change is zero or negative.
