# Q0215: get-full-position via borrow: have the same quantity scaled twice by two contracts that 

## Question
`get-full-position` (mainnet/contracts/market/v0-4-market.clar:470) returns all collateral rows regardless of the enabled bitmap. Can an unprivileged caller of `borrow` (mainnet/contracts/market/v0-4-market.clar:1238), by choosing the future mask produced by the new debt bit, use that to have the same quantity scaled twice by two contracts that round differently, violating the invariant that shares outstanding valued at the current share price never exceed `total-assets` and producing protocol insolvency through uncollateralised debt?

## Target
- File/function: `mainnet/contracts/market/v0-4-market.clar:470` -> `get-full-position`
- Entrypoint: `borrow` (`mainnet/contracts/market/v0-4-market.clar:1238`), unprivileged and publicly callable
- Attacker controls: the future mask produced by the new debt bit
- Exploit idea: `get-full-position` returns all collateral rows regardless of the enabled bitmap. Reach it through `borrow` and have the same quantity scaled twice by two contracts that round differently.
- Invariant to test: shares outstanding valued at the current share price never exceed `total-assets`
- Expected Immunefi impact: Critical - protocol insolvency through uncollateralised debt
- Fast validation: Run the baseline `borrow` call, then the attacker-shaped one with the future mask produced by the new debt bit, and assert the attacker's net token balance change is zero or negative.
