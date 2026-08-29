# Q3011: resolve-callcode via supply-collateral-add: count one deposit as backing for two simultaneous claims

## Question
`resolve-callcode` (mainnet/contracts/market/v0-4-market.clar:349) chains callcode transforms, with CALLCODE-ZSTSTX composing `resolve-ztoken` over `resolve-ststx`. Can an unprivileged caller of `supply-collateral-add` (mainnet/contracts/market/v0-4-market.clar:1175), by choosing vault share price at the moment of the deposit leg, use that to count one deposit as backing for two simultaneous claims, violating the invariant that tokens held by .v0-market-vault equal the sum of its `collateral` map for that asset and producing protocol insolvency through uncollateralised debt?

## Target
- File/function: `mainnet/contracts/market/v0-4-market.clar:349` -> `resolve-callcode`
- Entrypoint: `supply-collateral-add` (`mainnet/contracts/market/v0-4-market.clar:1175`), unprivileged and publicly callable
- Attacker controls: vault share price at the moment of the deposit leg
- Exploit idea: `resolve-callcode` chains callcode transforms, with CALLCODE-ZSTSTX composing `resolve-ztoken` over `resolve-ststx`. Reach it through `supply-collateral-add` and count one deposit as backing for two simultaneous claims.
- Invariant to test: tokens held by .v0-market-vault equal the sum of its `collateral` map for that asset
- Expected Immunefi impact: Critical - protocol insolvency through uncollateralised debt
- Fast validation: Run the baseline `supply-collateral-add` call, then the attacker-shaped one with vault share price at the moment of the deposit leg, and assert the attacker's net token balance change is zero or negative.
