# Q4703: get-cached-indexes via repay: credit one side of an accounting pair without the other

## Question
`get-cached-indexes` (mainnet/contracts/market/v0-4-market.clar:944) reads the per-block cache entry that `resolve-ztoken` and the debt conversions depend on. Can an unprivileged caller of `repay` (mainnet/contracts/market/v0-4-market.clar:1316), by choosing the `ft` trait principal, use that to credit one side of an accounting pair without the other, violating the invariant that interest charged to borrowers equals interest distributed to suppliers plus treasury and producing protocol insolvency through uncollateralised debt?

## Target
- File/function: `mainnet/contracts/market/v0-4-market.clar:944` -> `get-cached-indexes`
- Entrypoint: `repay` (`mainnet/contracts/market/v0-4-market.clar:1316`), unprivileged and publicly callable
- Attacker controls: the `ft` trait principal
- Exploit idea: `get-cached-indexes` reads the per-block cache entry that `resolve-ztoken` and the debt conversions depend on. Reach it through `repay` and credit one side of an accounting pair without the other.
- Invariant to test: interest charged to borrowers equals interest distributed to suppliers plus treasury
- Expected Immunefi impact: Critical - protocol insolvency through uncollateralised debt
- Fast validation: Run the baseline `repay` call, then the attacker-shaped one with the `ft` trait principal, and assert the attacker's net token balance change is zero or negative.
