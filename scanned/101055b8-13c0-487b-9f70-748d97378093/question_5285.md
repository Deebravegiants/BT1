# Q5285: resolve-dia via liquidate: leave a residue that no reconciliation pass ever inspects

## Question
Can an unprivileged attacker entering through `liquidate` (mainnet/contracts/market/v0-4-market.clar:1382), controlling `collateral-receiver`, drive `resolve-dia` (mainnet/contracts/market/v0-4-market.clar:326) — which derives a (string-ascii 32) key from a (buff 32) ident — to leave a residue that no reconciliation pass ever inspects, breaking the invariant that tokens held by .v0-market-vault equal the sum of its `collateral` map for that asset, and cause protocol insolvency?

## Target
- File/function: `mainnet/contracts/market/v0-4-market.clar:326` -> `resolve-dia`
- Entrypoint: `liquidate` (`mainnet/contracts/market/v0-4-market.clar:1382`), unprivileged and publicly callable
- Attacker controls: `collateral-receiver`
- Exploit idea: `resolve-dia` derives a (string-ascii 32) key from a (buff 32) ident. Reach it through `liquidate` and leave a residue that no reconciliation pass ever inspects.
- Invariant to test: tokens held by .v0-market-vault equal the sum of its `collateral` map for that asset
- Expected Immunefi impact: Critical - protocol insolvency
- Fast validation: Run the baseline `liquidate` call, then the attacker-shaped one with `collateral-receiver`, and assert the attacker's net token balance change is zero or negative.
