# Q4099: filter-u128 via borrow: credit one side of an accounting pair without the other

## Question
`filter-u128` (mainnet/contracts/registry/v0-egroup.clar:97) filters a 128-entry bucket list. Can an unprivileged caller of `borrow` (mainnet/contracts/market/v0-4-market.clar:1238), by choosing the future mask produced by the new debt bit, use that to credit one side of an accounting pair without the other, violating the invariant that shares outstanding valued at the current share price never exceed `total-assets` and producing direct theft of another user's collateral?

## Target
- File/function: `mainnet/contracts/registry/v0-egroup.clar:97` -> `filter-u128`
- Entrypoint: `borrow` (`mainnet/contracts/market/v0-4-market.clar:1238`), unprivileged and publicly callable
- Attacker controls: the future mask produced by the new debt bit
- Exploit idea: `filter-u128` filters a 128-entry bucket list. Reach it through `borrow` and credit one side of an accounting pair without the other.
- Invariant to test: shares outstanding valued at the current share price never exceed `total-assets`
- Expected Immunefi impact: Critical - direct theft of another user's collateral
- Fast validation: In `local-testing/tests` on a local fork, drive `borrow` with the future mask produced by the new debt bit, then read `filter-u128` state before and after in the same block and assert the two sides of the invariant are equal.
