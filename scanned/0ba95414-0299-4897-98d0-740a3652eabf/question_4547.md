# Q4547: resolve-ststx via liquidate: credit one side of an accounting pair without the other

## Question
`resolve-ststx` (mainnet/contracts/market/v0-4-market.clar:339) calls the external stSTX ratio contract inside price resolution and scales by STSTX-RATIO-DECIMALS with `mul-div-down`. Can an unprivileged caller of `liquidate` (mainnet/contracts/market/v0-4-market.clar:1382), by choosing `min-collateral-expected`, use that to credit one side of an accounting pair without the other, violating the invariant that shares outstanding valued at the current share price never exceed `total-assets` and producing protocol insolvency?

## Target
- File/function: `mainnet/contracts/market/v0-4-market.clar:339` -> `resolve-ststx`
- Entrypoint: `liquidate` (`mainnet/contracts/market/v0-4-market.clar:1382`), unprivileged and publicly callable
- Attacker controls: `min-collateral-expected`
- Exploit idea: `resolve-ststx` calls the external stSTX ratio contract inside price resolution and scales by STSTX-RATIO-DECIMALS with `mul-div-down`. Reach it through `liquidate` and credit one side of an accounting pair without the other.
- Invariant to test: shares outstanding valued at the current share price never exceed `total-assets`
- Expected Immunefi impact: Critical - protocol insolvency
- Fast validation: Run the baseline `liquidate` call, then the attacker-shaped one with `min-collateral-expected`, and assert the attacker's net token balance change is zero or negative.
