# Q0499: get-bitmap via borrow: have the same quantity scaled twice by two contracts that 

## Question
`get-bitmap` (mainnet/contracts/registry/v0-assets.clar:145) returns the global enabled bitmap that every position read filters on. Can an unprivileged caller of `borrow` (mainnet/contracts/market/v0-4-market.clar:1238), by choosing `amount`, use that to have the same quantity scaled twice by two contracts that round differently, violating the invariant that interest charged to borrowers equals interest distributed to suppliers plus treasury and producing direct theft of another user's collateral?

## Target
- File/function: `mainnet/contracts/registry/v0-assets.clar:145` -> `get-bitmap`
- Entrypoint: `borrow` (`mainnet/contracts/market/v0-4-market.clar:1238`), unprivileged and publicly callable
- Attacker controls: `amount`
- Exploit idea: `get-bitmap` returns the global enabled bitmap that every position read filters on. Reach it through `borrow` and have the same quantity scaled twice by two contracts that round differently.
- Invariant to test: interest charged to borrowers equals interest distributed to suppliers plus treasury
- Expected Immunefi impact: Critical - direct theft of another user's collateral
- Fast validation: In `local-testing/tests` on a local fork, drive `borrow` with `amount`, then read `get-bitmap` state before and after in the same block and assert the two sides of the invariant are equal.
