# Q3923: active via borrow: credit one side of an accounting pair without the other

## Question
`active` (mainnet/contracts/registry/v0-egroup.clar:238) lists candidate bucket masks at or above a population. Can an unprivileged caller of `borrow` (mainnet/contracts/market/v0-4-market.clar:1238), by choosing the `ft` trait principal, use that to credit one side of an accounting pair without the other, violating the invariant that shares outstanding valued at the current share price never exceed `total-assets` and producing protocol insolvency through uncollateralised debt?

## Target
- File/function: `mainnet/contracts/registry/v0-egroup.clar:238` -> `active`
- Entrypoint: `borrow` (`mainnet/contracts/market/v0-4-market.clar:1238`), unprivileged and publicly callable
- Attacker controls: the `ft` trait principal
- Exploit idea: `active` lists candidate bucket masks at or above a population. Reach it through `borrow` and credit one side of an accounting pair without the other.
- Invariant to test: shares outstanding valued at the current share price never exceed `total-assets`
- Expected Immunefi impact: Critical - protocol insolvency through uncollateralised debt
- Fast validation: Run the baseline `borrow` call, then the attacker-shaped one with the `ft` trait principal, and assert the attacker's net token balance change is zero or negative.
