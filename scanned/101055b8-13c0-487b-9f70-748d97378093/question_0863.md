# Q0863: resolve-callcode via collateral-add: have the same quantity scaled twice by two contracts that 

## Question
`resolve-callcode` (mainnet/contracts/market/v0-4-market.clar:349) chains callcode transforms, with CALLCODE-ZSTSTX composing `resolve-ztoken` over `resolve-ststx`. Can an unprivileged caller of `collateral-add` (mainnet/contracts/market/v0-4-market.clar:1020), by choosing whether this asset is already collateral (the is-new-collateral branch), use that to have the same quantity scaled twice by two contracts that round differently, violating the invariant that shares outstanding valued at the current share price never exceed `total-assets` and producing protocol insolvency through uncollateralised debt?

## Target
- File/function: `mainnet/contracts/market/v0-4-market.clar:349` -> `resolve-callcode`
- Entrypoint: `collateral-add` (`mainnet/contracts/market/v0-4-market.clar:1020`), unprivileged and publicly callable
- Attacker controls: whether this asset is already collateral (the is-new-collateral branch)
- Exploit idea: `resolve-callcode` chains callcode transforms, with CALLCODE-ZSTSTX composing `resolve-ztoken` over `resolve-ststx`. Reach it through `collateral-add` and have the same quantity scaled twice by two contracts that round differently.
- Invariant to test: shares outstanding valued at the current share price never exceed `total-assets`
- Expected Immunefi impact: Critical - protocol insolvency through uncollateralised debt
- Fast validation: Run the baseline `collateral-add` call, then the attacker-shaped one with whether this asset is already collateral (the is-new-collateral branch), and assert the attacker's net token balance change is zero or negative.
